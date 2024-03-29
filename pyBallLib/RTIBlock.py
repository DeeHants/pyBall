__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

from .Constants import Ops, Addr


class RTIBlock:
    def __init__(self, sequence, index: int):
        self._sequence = sequence
        self._bank = sequence._bank
        self._zone = sequence._bank._zone
        self._connection = sequence._bank._zone._connection
        self._index = index

        self.data = []
        self.length = 0
        self.width = 73
        self.height = 73
        self.offset = 0  # Updated when uploaded

    @property
    def index(self):
        """Return the index of this RTI block"""
        return self._index

    def upload(self, offset: int):
        print("Uploading B{bank}S{sequence}R{image}".format(
            bank=self._bank.index,
            sequence=self._sequence.index,
            image=self._index,
        ))
        # No image to upload

        # Store the offset for the metadata
        self.offset = offset

    def upload_metadata(self):
        self._connection.send(
            Ops.STORE, Addr.IMAGE_BASE + (self._index * 4), self._sequence.bs,
            [
                self.width,
                0,  # FIXME What is 0?
                self.offset,
                0x00FF  # FIXME What is 0xff?
            ]
        )
