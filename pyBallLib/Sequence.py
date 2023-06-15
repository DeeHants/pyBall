__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

from .Constants import Ops, Addr
from .Image import Image
from .Position import Position
from .RTIBlock import RTIBlock


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

    def append_image(self, width, image_filename='', image_data=[], image_bytes=[]):
        image = Image(self, len(self.images), width, image_filename, image_data, image_bytes)
        self.images.append(image)
        self._renumber_images()
        return image

    def _renumber_images(self):
        for index in range(len(self.images)):
            self.images[index].index = index

    def append_position(self):
        position = Position(self, len(self.positions))
        self.positions.append(position)
        self._renumber_positions()
        return position

    def _renumber_positions(self):
        for index in range(len(self.positions)):
            self.positions[index].index = index

    def bs(self):
        return self.bank.bs() | self.index

    def upload(self, connection):
        print("Uploading B{bank}S{sequence}".format(
            bank=self.bank.index,
            sequence=self.index,
        ))
        self.upload_images(connection)
        self.upload_positions(connection)

    def upload_images(self, connection):
        self.bank.zone.target(connection, True)

        # Reset the running sum for image checksum
        connection.running_sum = 0

        # Upload each image
        offset = Addr.DATA_BASE
        for image in self.images:
            image.upload(connection, offset)
            offset += image.length

        print("Uploading B{bank}S{sequence}Imd".format(
            bank=self.bank.index,
            sequence=self.index,
        ))
        # Set the image metadata
        offset = Addr.DATA_BASE
        bs = self.bs()
        for index in range(256):
            if index < len(self.images):
                # Image entry
                image = self.images[index]
                image.upload_metadata(connection)
                offset = image.offset + image.length
            else:
                # No image
                connection.send(Ops.STORE, Addr.IMAGE_BASE + (index * 4), bs,
                                [0, 0, offset, 0x00FF])  # FIXME What is 0, and 0xff?

        print("Uploading B{bank}S{sequence}Ics".format(
            bank=self.bank.index,
            sequence=self.index,
        ))
        # Save the image checksum
        sum = connection.running_sum
        sum_hi = int((sum & 0xffff0000) >> 16)
        sum_lo = (sum & 0x0000ffff)
        connection.send(Ops.STORE, 0x2003, bs, [sum_hi, sum_lo])

        self.bank.zone.target(connection, False)

    def upload_positions(self, connection):
        self.bank.zone.target(connection, True)

        # Upload each position
        for position in self.positions:
            position.uploadbulk(connection)

        # Blank out the next position
        print("Uploading B{bank}S{sequence}PX".format(
            bank=self.bank.index,
            sequence=self.index,
        ))
        bs = self.bs()
        connection.send(Ops.STORE, Addr.POSITION_BASE + (len(self.positions) << 4), bs,
                        [0x0000, 0x0100, 0x0000, 0x00FF, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x1023, 0x0201, 0x0001, 0x0000, 0x0009])

        # Upload each position (additional attributes)
        for position in self.positions:
            position.upload(connection)

        # Update sequence parameters
        connection.send(Ops.STORE, 0x2002, bs, [len(self.positions)])
        connection.send(Ops.STORE, 0x2001, bs, [self.repeat - 1])

        self.bank.zone.target(connection, False)
