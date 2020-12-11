from .Constants import Ops, Addr


class RTIBlock:
    def __init__(self, sequence, index):
        self.sequence = sequence
        self.index = index

        self.data = []
        self.length = 0
        self.width = 73
        self.height = 73
        self.offset = 0  # Updated when uploaded

    def upload(self, connection, offset):
        print("Uploading B{bank}S{sequence}R{image}".format(
            bank=self.sequence.bank.index,
            sequence=self.sequence.index,
            image=self.index,
        ))
        # No image to upload

        # Store the offset for the metadata
        self.offset = offset

    def upload_metadata(self, connection):
        bs = self.sequence.bs()
        connection.send(Ops.STORE, Addr.IMAGE_BASE + (self.index * 4), bs,
                        [self.width, 0, self.offset, 0x00FF])  # FIXME What is 0, and 0xff?
