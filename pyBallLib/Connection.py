import binascii
import re
import struct
import serial

from .Constants import Ops, Addr

class Connection:
    def __init__(self, port):
        self.serial_pattern = re.compile('[0-9a-f]{16}', re.IGNORECASE)

        self.ser = serial.Serial(port, 38400)
        pass

    def target(self, serial, channel, enable):
        self.send(Ops.TARGET, 0x0000, 0x0000, [serial, channel, 0x1 if enable else 0x0])

    def set(self, bank, sequence, position, parameter, value):
        # Address 1 is the low nibble specifying the parameter, and subsequent positions following on from 0x2100
        parameter += Addr.POSITION_BASE + (position.index << 4)
        # Address 2 has the sequence index (0-16) in the low nibble, and the bank index above that
        bank_sequence = (bank.index << 4) | sequence.index

        self.send(Ops.OP_SET_ADDR, parameter, bank_sequence, value)

    def send(self, op, addr, addr2 = 0, data = 0):
        # Check parameters are valid
        if not isinstance(op, int): raise TypeError('Parameter "op" is not an <int>.')
        if op < 0x00 or op > 0xff: raise ValueError('Parameter "op" is out of range. Must be 0 to 255.')
        if not isinstance(addr, int): raise TypeError('Parameter "addr" is not an <int>.')
        if addr < 0x0000 or addr > 0xffff: raise ValueError('Parameter "addr" is out of range. Must be 0 to 65535.')
        if not isinstance(addr2, int): raise TypeError('Parameter "addr2" is not an <int>.')
        if addr2 < 0x0000 or addr2 > 0xffff: raise ValueError('Parameter "addr2" is out of range. Must be 0 to 65535.')

        # Convert the data into an array of 16-bit signed integers
        data_array = [];
        # First, if it's not a list, make it a list of the one item
        if not isinstance(data, list): data = [data]
        for item in data:
            if isinstance(item, int) and not (addr2 < 0x0000 or addr2 > 0xffff):
                # data is an int in the range of a 16-bit signed integer
                data_array.append(item);

            elif isinstance(item, str) and len(item) == 16 and self.serial_pattern.match(item):
                # Serial numbers (16 char hex string) are treated specially
                for offset in [12, 8, 4, 0]:
                    data_array.append(int(item[offset:offset + 4], 16));

            else:
                # Anything we're not sure about, raise an error
                raise ValueError('Parameter "data[' + str(item) + ']" is not supported.')

        # Calculate the length and checksum
        length = len(data_array)
        sum = op + addr + addr2 + length
        for block in data_array: sum += block
        sum &= 0xffff

        # Convert to an array of bytes supported by pack
        data_bytes = struct.pack('<' + (length * 'H'), *data_array)
        # And then to the final blob of data
        result = struct.pack('<BHHH' + str(len(data_bytes)) + 'sH', op, addr, addr2, length, data_bytes, sum)

        # Print the result
        # hex = binascii.hexlify(result)
        hex = ' '.join(format(x, '02X') for x in bytearray(result))
        print('Length ' + str(len(result)) + ': ' + hex)

        self.ser.write(result)
