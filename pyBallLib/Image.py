import struct

from .Constants import Ops, Addr


class Image:
    def __init__(self, sequence, index, width, image_filename='', image_data=[], image_bytes=[]):
        self.sequence = sequence
        self.index = index

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
            image_data = [0] * (0x10 * 73)

        # Validate the array size
        if len(image_data) != (width * 0x10):
            raise ValueError("Image data size ({size}) does not match expected size ({expected_size})".format(
                size=len(image_data),
                expected_size=width * 0x10,
            ))

        self.data = image_data
        self.length = len(self.data)
        self.width = width
        self.height = 73
        self.offset = 0  # Updated when uploaded

        # Generate the pixel map
        self.pixel_map = []
        offset_counter = 0
        for index in range(73):
            pixel_data = (
                # Red
                (offset_counter) % 0x10,
                int((offset_counter) / 0x10),

                # Green
                (offset_counter + 1) % 0x10,
                int((offset_counter + 1) / 0x10),

                # Blue
                (offset_counter + 2) % 0x10,
                int((offset_counter + 2) / 0x10),
            )
            self.pixel_map.append(pixel_data)

            # Increment the count, allowing for the 5 bit gap between the 65th and 66th pixel
            offset_counter += 3
            if index == 64:
                offset_counter += 5

    def set_pixel(self, x, y, r, g, b):
        x_offset = (x * 0x10)
        pixel_data = self.pixel_map[y]

        # Red
        index = x_offset + pixel_data[0]
        pattern = 1 << pixel_data[1]
        pattern2 = (~pattern) & 0xffff
        if r:
            self.data[index] |= pattern
        else:
            self.data[index] &= pattern2

        # Green
        index = x_offset + pixel_data[2]
        pattern = 1 << pixel_data[3]
        pattern2 = (~pattern) & 0xffff
        if g:
            self.data[index] |= pattern
        else:
            self.data[index] &= pattern2

        # Blue
        index = x_offset + pixel_data[4]
        pattern = 1 << pixel_data[5]
        pattern2 = (~pattern) & 0xffff
        if b:
            self.data[index] |= pattern
        else:
            self.data[index] &= pattern2

    def upload(self, connection, offset):
        print("Uploading B{bank}S{sequence}I{image}".format(
            bank=self.sequence.bank.index,
            sequence=self.sequence.index,
            image=self.index,
        ))
        # Set the image
        bs = self.sequence.bs()
        for index in range(0, len(self.data), 0x10):
            connection.send(Ops.STORE, offset + index, bs, self.data[index:index + 0x10])

        # Store the offset for the metadata
        self.offset = offset

    def upload_col(self, connection, col):
        x_offset = (col * 0x10)

        print("Uploading B{bank}S{sequence}I{image}C{col}".format(
            bank=self.sequence.bank.index,
            sequence=self.sequence.index,
            image=self.index,
            col=col,
        ))
        # Set the image column
        connection.send(Ops.STORE, self.offset + x_offset, self.sequence.bs(),
                        self.data[x_offset:x_offset + 0x10])

    def upload_metadata(self, connection):
        bs = self.sequence.bs()
        connection.send(Ops.STORE, Addr.IMAGE_BASE + (self.index * 4), bs,
                        [self.width, 0, self.offset, 0x00FF])  # FIXME What is 0, and 0xff?
