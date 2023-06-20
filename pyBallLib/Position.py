__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

from .Constants import Ops, Addr


class Position:
    def __init__(self, sequence, index: int):
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

    def upload(self):
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

    def upload_repeat(self):
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

# Cols  1
# Length 11: 02 01 21 00 00 01 00 22 01 26 22

# Gap   2
# Length 11: 02 02 21 00 00 01 00 20 00 25 21

# Brilliance 3
# Length 11: 02 03 21 00 00 01 00 FF 00 05 22

# Scroll 4
# Length 11: 02 04 21 00 00 01 00 00 00 07 21

# Position 5
# Length 11: 02 05 21 00 00 01 00 00 00 08 21

# Flash 9 low
# Length 11: 02 09 21 00 00 01 00 00 00 0C 21 # none
# Length 11: 02 09 21 00 00 01 00 40 00 4C 21 # slow

# Wipe 9 high
# Length 11: 02 09 21 00 00 01 00 00 01 0C 22 # wipe slow
# Length 11: 02 09 21 00 00 01 00 00 04 0C 25 # wipe med
# Length 11: 02 09 21 00 00 01 00 00 00 0C 21 # wipe off

# Fade in A low
# Length 11: 02 0A 21 00 00 01 00 00 00 0D 21
# Length 11: 02 0A 21 00 00 01 00 10 00 1D 21 # fade slow
# Length 11: 02 0A 21 00 00 01 00 08 00 15 21 # fade med
# Length 11: 02 0A 21 00 00 01 00 00 00 0D 21 # fade off

# Fade out A high
# Length 11: 02 0A 21 00 00 01 00 00 00 0D 21
# Length 11: 02 0A 21 00 00 01 00 00 10 0D 31 # fade slow
# Length 11: 02 0A 21 00 00 01 00 00 08 0D 29 # fade med
# Length 11: 02 0A 21 00 00 01 00 00 00 0D 21 # fade off

# Frames F
# Length 11: 02 0F 21 00 00 01 00 F9 00 0B 22
