import numpy as np
import serial
import time

from pga460_header import *

# list of addresses we don't want to overwrite
# frequency, ee_crc, ee_cntrl, dev_stat1, dev_stat2
#  These registers are written automatically by the device, and thus we do not set them manually
black_list = [28, 43, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 77]
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
            # Catch before the EOF on line 91 of param file
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
    amplitude = np.uint8(result[4])
    width = np.uint8(result[3])

    results = [distance, amplitude, width]

    return results

def get_resonant_frequency(port):
    ser = open_serial(port)
    buf_tx = [pga460.SD]
    buf_tx.insert(0, pga460.SYNCBYTE)
    ser.write(buf_tx)
    result = ser.read(4)

    freq = 1000000 / (result[1] * 500)
    reg_val = round((freq - 30) / 0.2)

    results = [freq, reg_val]
    return results

def sweep_for_best_frequency(port):
    freq = get_resonant_frequency(port)
    averaged_measurements_list = []
    # Look at the 10 frequency below the diagnostic and 10 above and use the best.
    for i in range(20):
        # Write a new driving frequency
        new_freq = freq[1] - 10 + i
        write_reg(port, 28, new_freq)

        # Take 6 measurements at the drive frequency, skip the first measurement and average the other 5
        ser = open_serial(port)
        measurements = []
        for j in range(6):
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
            # Skip first measurement, and do no include measurements that are 0xFF
            if j > 0:
                if result[4] < 255:
                    measurements.append(result[4])
        ser.close()

        # Average the measurements and print the average
        print("Register value: %d   AvgAmplitude: %d" % (new_freq, np.mean(measurements)))
        averaged_measurements_list.append(np.mean(measurements))

    maximum_amplitude = max(averaged_measurements_list)
    index_of_largest = averaged_measurements_list.index(maximum_amplitude)
    best_drive_freq_reg_val = freq[1] - 10 + index_of_largest

    print("\nRegister value: %d   AvgAmplitude: %d" % (best_drive_freq_reg_val, maximum_amplitude))
    write_reg(port, 28, best_drive_freq_reg_val)

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

