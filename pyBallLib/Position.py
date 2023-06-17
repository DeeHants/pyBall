__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

from .Constants import Ops, Addr


class Position:
    def __init__(self, sequence, index):
        self._sequence = sequence
        self._bank = sequence._bank
        self._zone = sequence._bank._zone
        self._connection = sequence._bank._zone._connection
        self.index = index

        self.image = 0
        self.columns = 73
        self.gap = 0
        self.brilliance = 0xff
        self.scroll = 0
        self.offset = 0
        self.repeat_index = 0
        self.repeat = 0
        self.flash_interval = 0
        self.wipe_increment = 0
        self.fade_in_increment = 0
        self.fade_out_increment = 0
        self.frames = 10

    def uploadbulk(self):
        print("Uploading B{bank}S{sequence}P{position}".format(
            bank=self._bank.index,
            sequence=self._sequence.index,
            position=self.index,
        ))

        base = Addr.POSITION_BASE + (self.index << 4)
        bs = self._sequence.bs()
        self._connection.send(
            Ops.STORE, base, bs,
            [
                self.image,
                self.columns,
                self.gap,
                self.brilliance,
                self.scroll,
                self.offset,
                self.repeat_index,
                self.repeat,
                0x0000,  # 0 # FIXME What is this?
                self.flash_interval | (self.wipe_increment << 8),
                self.fade_in_increment | (self.fade_out_increment << 8),
                0x1023,  # 4131 # FIXME What is this?
                0x0201,  # 513 # FIXME What is this?
                0x0001,  # 1 # FIXME What is this?
                0x0000,  # 0 # FIXME What is this?
                self.frames - 1,
            ]
        )

    def upload(self):
        print("Uploading B{bank}S{sequence}P{position}b".format(
            bank=self._bank.index,
            sequence=self._sequence.index,
            position=self.index,
        ))

        base = Addr.POSITION_REPEAT_INDEX + (self.index << 4)  # and POSITION_REPEAT_COUNT
        bs = self._sequence.bs()
        self._connection.send(
            Ops.STORE, base, bs,
            [
                self.repeat_index,
                self.repeat
            ]
        )
