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
