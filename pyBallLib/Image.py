__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

import struct

from .Constants import Ops, Addr


class Image:
    WORDS_PER_COLUMN = 0x10  # 16x 16-bit words per column

    def __init__(self, sequence, index: int, width: int, image_filename: str = '', image_data=[], image_bytes=[]):
        self._sequence = sequence
        self._bank = sequence._bank
        self._zone = sequence._bank._zone
        self._connection = sequence._bank._zone._connection
        self._index = index

        # Open the image file
        if image_filename:
            image_file = open(image_filename, 'rb')
            image_bytes = image_file.read()
            image_file.close()

        # Repack the bytes into the array of 16-bit words
        if len(image_bytes):
            image_data = []
            for index in range(len(image_bytes) // 2):
                image_data.append(struct.unpack_from('<H', image_bytes, index * 2)[0])

        # Create the data array if not already done
        if len(image_data) == 0:
            image_data = [0] * (self.WORDS_PER_COLUMN * width)

        # Validate the array size
        if len(image_data) != (self.WORDS_PER_COLUMN * width):
            raise ValueError("Image data size ({size}) does not match expected size ({expected_size})".format(
                size=len(image_data),
                expected_size=self.WORDS_PER_COLUMN * width,
            ))

        self.data = image_data
        self.length = len(self.data)
        self.width = width
        self.height = 73
        self.offset = 0  # Updated when uploaded

        # Generate the pixel map to index each component of each pixel in the column data
        self.pixel_map = []
        offset_counter = 0
        for index in range(73):
            pixel_data = (
                # Red
                (offset_counter) % self.WORDS_PER_COLUMN,  # Word offset
                int((offset_counter) / self.WORDS_PER_COLUMN),  # Bit position

                # Green
                (offset_counter + 1) % self.WORDS_PER_COLUMN,  # Word offset
                int((offset_counter + 1) / self.WORDS_PER_COLUMN),  # Bit position

                # Blue
                (offset_counter + 2) % self.WORDS_PER_COLUMN,  # Word offset
                int((offset_counter + 2) / self.WORDS_PER_COLUMN),  # Bit position
            )
            self.pixel_map.append(pixel_data)

            # Increment the count, allowing for the 5 bit gap between the 65th and 66th pixel
            offset_counter += 3
            if index == 64:
                offset_counter += 5

    @property
    def index(self):
        """Return the index of this image"""
        return self._index

    def set_pixel(self, x: int, y: int, colour: tuple):
        # Check the tuple length
        if len(colour) != 3:
            raise ValueError("colour value must contain 3 elements")

        x_offset = (x * self.WORDS_PER_COLUMN)
        pixel_data = self.pixel_map[y]

        # Red
        index = x_offset + pixel_data[0]
        pattern = 1 << pixel_data[1]
        pattern2 = (~pattern) & 0xffff
        if colour[0]:
            self.data[index] |= pattern
        else:
            self.data[index] &= pattern2

        # Green
        index = x_offset + pixel_data[2]
        pattern = 1 << pixel_data[3]
        pattern2 = (~pattern) & 0xffff
        if colour[1]:
            self.data[index] |= pattern
        else:
            self.data[index] &= pattern2

        # Blue
        index = x_offset + pixel_data[4]
        pattern = 1 << pixel_data[5]
        pattern2 = (~pattern) & 0xffff
        if colour[2]:
            self.data[index] |= pattern
        else:
            self.data[index] &= pattern2

    def upload(self, offset: int):
        print("Uploading B{bank}S{sequence}I{image}".format(
            bank=self._bank.index,
            sequence=self._sequence.index,
            image=self._index,
        ))
        # Set the image
        bs = self._sequence.bs()
        for index in range(0, len(self.data), self.WORDS_PER_COLUMN):
            self._connection.send(
                Ops.STORE, offset + index, bs,
                self.data[index:index + self.WORDS_PER_COLUMN]
            )

        # Store the offset for the metadata
        self.offset = offset

    def upload_col(self, col: int):
        x_offset = (col * self.WORDS_PER_COLUMN)

        print("Uploading B{bank}S{sequence}I{image}C{col}".format(
            bank=self._bank.index,
            sequence=self._sequence.index,
            image=self._index,
            col=col,
        ))
        # Set the image column
        self._connection.send(
            Ops.STORE, self.offset + x_offset, self._sequence.bs(),
            self.data[x_offset:x_offset + self.WORDS_PER_COLUMN]
        )

    def upload_metadata(self):
        bs = self._sequence.bs()
        self._connection.send(
            Ops.STORE, Addr.IMAGE_BASE + (self._index * 4), bs,
            [
                self.width,
                0,  # FIXME What is 0?
                self.offset,
                0x00FF  # FIXME What is 0xff?
            ]
        )
