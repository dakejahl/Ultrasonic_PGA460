import numpy as np
import serial
import time

from pga460_header import *


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

def write_eeprom(port, file_name):
    with open(file_name, "r") as params:
        line_count = 0
        ser = open_serial(port)
        for line in params:
            line_count = line_count + 1
            addr = int(params.read(2), 16)
            while params.read(1) != ',':
                pass
            val = int(params.read(2), 16)

            # We will now write the val to the addr
            buf_tx = [pga460.SRW, addr, val]
            checksum = calc_checksum(buf_tx, len(buf_tx))
            # Put the SYNCBYTE at the front and the checksum at the end
            buf_tx.insert(0, pga460.SYNCBYTE)
            buf_tx.append(checksum)

            ser.write(buf_tx)

            print("%d  %s" % (addr, hex(val)))
            if line_count == 91:
                ser.close()
                return 1
    return 0



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
