import numpy as np
import serial
import time

from pga460_header import *

# list of addresses we don't want to overwrite
# frequency, ee_crc, ee_cntrl, dev_stat1, dev_stat2
black_list = [28, 43, 64, 76, 77]
# black_list = [0]

def print_usage():
    print('\nCommands:')
    print('    port(path)            Sets the port.                                 e.g: port com15             ')
    print('    params(file_name)     Writes the parameters from the file.           e.g: params golden_file.txt ')
    print('    measure               Saves the eeproms state.                       e.g: save                   ')
    print('    diag                  Saves the eeproms state.                       e.g: save                   ')
    print('    write(addr, val)      Writes the value to the address.               e.g: write 0 55             ')
    print('    read(addr)            Reads the value at the address.                e.g: read 0                 ')
    print('    save                  Saves the eeproms state.                       e.g: save                   ')



def open_serial(port):
    # configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
    port=port,
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
    )
    return ser

def write_reg(port, reg, val):
    buf_tx = [pga460.SRW, reg, val]
    checksum = calc_checksum(buf_tx, len(buf_tx))
    # Put the SYNCBYTE at the front and the checksum at the end
    buf_tx.insert(0, pga460.SYNCBYTE)
    buf_tx.append(checksum)

    ser = open_serial(port)
    ser.write(buf_tx)
    ser.close()

def read_reg(port, reg):
    buf_tx = [pga460.SRR, reg]
    checksum = calc_checksum(buf_tx, len(buf_tx))
    # Put the SYNCBYTE at the front and the checksum at the end
    buf_tx.insert(0, pga460.SYNCBYTE)
    buf_tx.append(checksum)

    ser = open_serial(port)
    ser.write(buf_tx)
    result = ser.read(3)
    ser.close()

    return result

def write_parameters(port, file_name):
    with open(file_name, "r") as params:
        line_count = 0
        count = 0
        ser = open_serial(port)
        # Parse the file line by line pulling out the address and value information
        for line in params:
            line_count = line_count + 1
            addr = int(params.read(2), 16)
            while params.read(1) != ',':
                pass
            val = int(params.read(2), 16)
            # Check if the current value matches the desired
            buf_tx = [pga460.SRR, addr]
            checksum = calc_checksum(buf_tx, len(buf_tx))
            buf_tx.insert(0, pga460.SYNCBYTE)
            buf_tx.append(checksum)

            ser.write(buf_tx)
            result = ser.read(3)

            # Only write the parameter if it is not already set
            if (int(result[1]) != val) and addr not in black_list:
                print('Address: %5s   Expected: %5s   Actual: %5s' % (addr, val, int(result[1])))

                # We will now write the val to the addr
                buf_tx = [pga460.SRW, addr, val]
                checksum = calc_checksum(buf_tx, len(buf_tx))
                buf_tx.insert(0, pga460.SYNCBYTE)
                buf_tx.append(checksum)

                ser.write(buf_tx)
                count = count + 1
            # There are 91 fields we must write, 43 of them are eeprom and persist after power up
            if line_count == 91:
                ser.close()
                return count
    return -1

def save_eeprom(port):
    # Unlock eeprom with the unlock code
    buf_tx = [pga460.SRW, pga460.EE_CNTRL_ADDR, pga460.EE_UNLOCK_ST1]
    checksum = calc_checksum(buf_tx, len(buf_tx))
    buf_tx.insert(0, pga460.SYNCBYTE)
    buf_tx.append(checksum)
    ser = open_serial(port)
    ser.write(buf_tx)
    ser.close()
    # Save eeprom memory
    buf_tx =  [pga460.SRW, pga460.EE_CNTRL_ADDR, pga460.EE_UNLOCK_ST2]
    checksum = calc_checksum(buf_tx, len(buf_tx))
    buf_tx.insert(0, pga460.SYNCBYTE)
    buf_tx.append(checksum)
    ser = open_serial(port)
    ser.write(buf_tx)
    ser.close()

def take_measurement(port):
    ser = open_serial(port)

    # First command a measurement
    buf_tx = [pga460.P1BL, 0x01]
    checksum = calc_checksum(buf_tx, len(buf_tx))
    buf_tx.insert(0, pga460.SYNCBYTE)
    buf_tx.append(checksum)
    ser.write(buf_tx)

    # Second command a collect
    buf_tx = [pga460.UMR]
    buf_tx.insert(0, pga460.SYNCBYTE)
    ser.write(buf_tx)
    # Third read the returned data
    result = ser.read(6)
    ser.close()

    time = (np.uint8(result[1]) << 8) + np.uint8(result[2])
    distance = time*0.000001*343/2
    print(distance)
    return distance

def get_resonant_frequency(port):
    ser = open_serial(port)
    buf_tx = [pga460.SD]
    buf_tx.insert(0, pga460.SYNCBYTE)
    ser.write(buf_tx)
    result = ser.read(4)
    print(result[1])
    print("Measured frequency: %2.2f" % round(1000000 / (result[1] * 500), 1))

    val = 1000000 / (result[1] * 500)

    freq_reg_val = round((val - 30) / 0.2)
    print("Value to write to register: %d" % freq_reg_val)

# TODO: Add a sweep for best frequency function. This function should narrow in on best drive frequency.
# TODO: Requires knowledge of surface and distance.

def calc_checksum(buf, len):
    carry = np.uint16(0x0000)

    for i in range(len):
        if (buf[i] + carry) < carry:
            carry = carry + buf[i] + 1
        else:
            carry = carry + buf[i]

    if carry > 0xFF:
        carry = carry - 255

    carry = (~carry & 0x00FF)
    return carry

