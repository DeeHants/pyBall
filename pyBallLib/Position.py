from .Constants import Ops, Addr


class Position:
    def __init__(self, sequence, index):
        self.bank = sequence.bank
        self.sequence = sequence
        self.index = index

        self.image = 0
        self.columns = 73
        self.gap = 0
        self.scroll = 0
        self.offset = 0
        self.repeat_index = 0
        self.repeat = 0
        self.frames = 10

    def uploadbulk(self, connection):
        print("Uploading B" + str(self.sequence.bank.index) + "S" +
              str(self.sequence.index) + "P" + str(self.index))

        data = [
            self.image,
            self.columns,
            self.gap,
            0xff,  # Brilliance
            self.scroll,
            self.offset,
            self.repeat_index,
            self.repeat,
            0x0000,  # 0
            0x0000,  # Position flash
            0x0000,  # 0
            0x1023,  # 4131
            0x0201,  # 513
            0x0001,  # 1
            0x0000,  # 0
            self.frames - 1,
        ]

        base = Addr.POSITION_BASE + (self.index << 4)
        bs = self.sequence.bs()
        connection.send(Ops.STORE, base, bs, data)

    def upload(self, connection):
        print("Uploading B" + str(self.sequence.bank.index) + "S" +
              str(self.sequence.index) + "P" + str(self.index) + "b")

        base = Addr.POSITION_BASE + (self.index << 4)
        bs = self.sequence.bs()
        connection.send(Ops.STORE, base + 0x6, bs, [self.repeat_index])
        connection.send(Ops.STORE, base + 0x7, bs, [self.repeat])
