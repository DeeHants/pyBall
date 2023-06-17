__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

from .Constants import Ops, Addr
from .Sequence import Sequence


class Bank:
    def __init__(self, zone, index):
        self._zone = zone
        self._connection = zone._connection
        self.index = index

        self.repeat = 1

        self._sequences = []
        for index in range(16):
            self._sequences.append(None)

    def sequence(self, index):
        try:
            # Ensure we have an object
            if not self._sequences[index]:
                self._sequences[index] = Sequence(self, index)

            # Return it
            return self._sequences[index]

        except IndexError:
            # Re-raise IndexError with a more useful message
            raise IndexError("sequence index out of range, must be 0-15")

    def bs(self):
        return self.index << 4

    def upload(self):
        print("Uploading B{bank}".format(
            bank=self.index,
        ))

        # Generate the base BS address
        bank_base = self.index << 4

        # Reset sequence states
        self._zone.target(True)

        for index in range(0x10):
            self._connection.send(
                Ops.STORE, Addr.SEQUENCE_STATE, self.bs() | index,
                [2]  # FIXME what is state 2?
            )
            self._connection.send(
                Ops.X8,  0x0000, 0x0000,  # FIXME What is op 8?
                [1]
            )
        self._zone.target(False)

        # Upload each sequence
        for sequence in self._sequences:
            if sequence:
                sequence.upload()

        # Set the state of uploaded sequences
        self._zone.target(True)
        for sequence in self._sequences:
            if sequence:
                self._connection.send(
                    Ops.STORE, Addr.SEQUENCE_STATE, sequence.bs(),
                    [3]  # FIXME what is state 3?
                )
        self._zone.target(False)
