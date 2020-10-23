from .Constants import Ops, Addr
from .Sequence import Sequence

class Bank:
    def __init__(self, zone, index):
        self.zone = zone
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
            raise IndexError('sequence index out of range, must be 0-15')

    def bs(self):
        return self.index << 4

    def upload(self, connection):
        print('Uploading B' + str(self.index))

        # Generate the base BS address
        bank_base = self.index << 4

        # Reset sequence states
        self.zone.target(connection, True)
        for index in range(0x10):
            connection.send(Ops.STORE, 0x2000, self.bs() | index, [2]) # FIXME what is state 2?
            connection.send(Ops.X8,  0x0000, 0x0000, [1]) # FIXME What is op 8?
        self.zone.target(connection, False)

        # Upload each sequence
        for sequence in self._sequences:
            if sequence:
                sequence.upload(connection)

        # Set the state of uploaded sequences
        self.zone.target(connection, True)
        for sequence in self._sequences:
            if sequence:
                connection.send(Ops.STORE, 0x2000, sequence.bs(), [3]) # FIXME what is state 2?
        self.zone.target(connection, False)
