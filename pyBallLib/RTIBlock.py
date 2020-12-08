from .Constants import Ops, Addr


class RTIBlock:
    def __init__(self, sequence, index):
        self.sequence = sequence
        self.index = index

        self.data = []
        self.length = 0
        self.height = 73  # TODO needed?
        self.width = 73

    def upload(self, connection, offset):
        print("Uploading B{bank}S{sequence}R{image}".format(
            bank=self.sequence.bank.index,
            sequence=self.sequence.index,
            image=self.index,
        ))
        # Set the image
        # for index in range(0, len(self.data), 0x10):
        #     connection.send(Constants.OP_SET_ADDR, offset + index, 0x0000, self.data[index:index + 0x10])
