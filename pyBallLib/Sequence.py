from .Constants import Ops, Addr
from .Image import Image
from .RTIBlock import RTIBlock
from .Position import Position

class Sequence:
    def __init__(self, bank, index):
        self.bank = bank
        self.index = index

        self.repeat = 1

        # Add 8 RTI blocks
        self.images = []
        for index in range(8):
            self.images.append(RTIBlock(self, index))

        # Empty position list
        self.positions = []

    def append_position(self):
        position = Position(self, 0)
        self.positions.append(position)
        self.renumber_positions()
        return position

    def renumber_positions(self):
        for index in range(len(self.positions)):
            self.positions[index].index = index

    def bs(self):
        return self.bank.bs() | self.index

    def upload(self, connection):
        print('Uploading B' + str(self.bank.index) + 'S' + str(self.index))

        self.bank.zone.target(connection, True)

        # Reset the running sum for image checksum
        connection.running_sum = 0

        # Upload each image
        offset = Addr.DATA_BASE
        for image in self.images:
            image.upload(connection, offset)
            offset += image.length

        print('Uploading B' + str(self.bank.index) + 'S' + str(self.index) + 'Imd')
        # Set the image metadata
        offset = Addr.DATA_BASE
        bs = self.bs()
        for index in range(256):
            if index < len(self.images):
                # Image entry
                image = self.images[index]
                connection.send(Ops.STORE, Addr.IMAGE_BASE + (index * 4), bs, [image.width, 0, offset, 0x00FF]) # FIXME What is 0, and 0xff?
                offset += image.length
            else:
                # No image
                connection.send(Ops.STORE, Addr.IMAGE_BASE + (index * 4), bs, [0, 0, offset, 0x00FF]) # FIXME What is 0, and 0xff?

        # Save the image checksum
        sum = connection.running_sum
        sum_hi = int((sum & 0xffff0000) >> 16)
        sum_lo = (sum & 0x0000ffff)
        connection.send(Ops.STORE, 0x2003, bs, [sum_hi, sum_lo])

        self.bank.zone.target(connection, False)

        self.bank.zone.target(connection, True)

        # Upload each position
        for position in self.positions:
            position.uploadbulk(connection)

        # Blank out the next position
        print('Uploading B' + str(self.bank.index) + 'S' + str(self.index) + 'PX')
        connection.send(Ops.STORE, Addr.POSITION_BASE + (len(self.positions) << 4), bs, [0x0000, 0x0100, 0x0000, 0x00FF, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1023, 0x0201, 0x0001, 0x0000, 0x0009])

        # Upload each position (additional attributes)
        for position in self.positions:
            position.upload(connection)

        # Update sequence parameters
        connection.send(Ops.STORE, 0x2002, bs, [len(self.positions)])
        connection.send(Ops.STORE, 0x2001, bs, [self.repeat - 1])

        self.bank.zone.target(connection, False)
