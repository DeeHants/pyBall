from .Constants import Ops, Addr

import struct

class Image:
    def __init__(self, sequence, index, image_filename=''):
        self.sequence = sequence
        self.index = index

        # Open the image file
        image_file = open(image_filename, 'rb')
        image_bytes = image_file.read()
        image_file.close()

        # Repack the bytes into the array of 16-bit words
        self.data = []
        for index in range(len(image_bytes) // 2):
            self.data.append(struct.unpack_from('<H', image_bytes, index * 2)[0])

        self.length = len(self.data)
        self.height = 73 #TODO needed?
        self.width = 100

    def upload(self, connection, offset):
        print('Uploading B' + str(self.sequence.bank.index) + 'S' + str(self.sequence.index) + 'I' + str(self.index))
        # Set the image
        bs = self.sequence.bs()
        for index in range(0, len(self.data), 0x10):
            connection.send(Ops.STORE, offset + index, bs, self.data[index:index + 0x10])
