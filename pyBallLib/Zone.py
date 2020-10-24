from .Constants import Ops, Addr
from .Bank import Bank

class Zone:
    def __init__(self):
        self.name = ''
        self.serial = ''
        self.channel = 0
        self.enabled = True
        self.chase_banks = True
        self.chase_bank_max = 4
        self.chase_sequences = True
        self.freeze = False
        self.scheduler = False

        self.active_bank = 0
        self.active_sequence = 0
        self.active_position = 0

        self._banks = []
        for index in range(4):
            self._banks.append(Bank(self, index))

    def updatestate(self, connection):
        state = 0
        if self.freeze: state |= 0x01
        if not self.chase_sequences: state |= 0x02
        if not self.chase_banks: state |= 0x04
        state |= (self.chase_bank_max << 8)

        connection.send(Ops.X7,  0x0000, 0x0000, [1]) # FIXME what is op 7?
        connection.send(Ops.STORE, 0x0108, 0x0000, [self.active_position, self.active_sequence, self.active_bank, state])
        connection.send(Ops.STORE, 0x010D, 0x0000, [self.scheduler])
        connection.send(Ops.X8,  0x0000, 0x0000, [1]) # FIXME what is op 8?

    def bank(self, index):
        try:
            # Ensure we have an object
            if not self._banks[index]:
                self._banks[index] = Bank(self, index)

            # Return it
            return self._banks[index]
        except IndexError:
            # Re-raise IndexError with a more useful message
            raise IndexError('bank index out of range, must be 0-3')

    def target(self, connection, enable):
        connection.target_zone(self.serial, self.channel, enable)

    def settime(self, connection):
        # Length 17: 04 BE 00 00 00 04 00 39 41 12 26 01 01 20 80 32 E9 # 12:41:39
        #           |op|     |     |len  |se|me|ho|da|mo|  |     |sum  |

        self.target(connection, True)
        connection.send(Ops.SETTIME, 0x00be, 0x0000, [0x4139, 0x2612, 0x0101, 0x8020]) # FIXME Correctly set time
        self.target(connection, False)

    def bs(self):
        return 0x0000

    def upload(self, connection):
        if self.serial == '': raise Exception("zone serial has not been set")

        # Set the initial state
        self.target(connection, True)
        self.chase_banks = False
        self.chase_sequences = False
        self.updatestate(connection)
        connection.send(Ops.STORE, 0x0106, 0x0000, [0]) # FIXME what is addr 0x0106?
        connection.send(Ops.STORE, 0x0107, 0x0000, [0]) # FIXME what is addr 0x0107?
        connection.send(Ops.STORE, 0x0105, 0x0000, [0]) # FIXME what is addr 0x0105?
        # FIXME preserve state
        self.chase_banks = True
        self.chase_sequences = True
        self.updatestate(connection)

        # Sync the time
        self.settime(connection)

        self.target(connection, True) # FIXME is this no-op needed?
        self.target(connection, False)

        # Upload each bank
        for bank in self._banks:
            if bank:
                bank.upload(connection)
                pass

        # Set the final state
        self.target(connection, True)
        connection.send(Ops.STORE, 0x0200, 0x0000, [0, 0, 0, 0]) # FIXME what is addr 0x0200?
        connection.send(Ops.STORE, 0x01FF, 0x0000, [0]) # FIXME what is addr 0x01ff?
        connection.send(Ops.STORE, 0x0180, 0x0000, [0, 0, 0, 0]) # FIXME what is addr 0x0180?
        self.chase_banks = False
        self.chase_sequences = False
        self.updatestate(connection)
        self.updatestate(connection) # FIXME 2nd time lucky?
        self.updatestate(connection) # FIXME 3rd time lucky?
        connection.send(Ops.REINIT, 0x0000, 0x0000, [1]) # Re-initialise
        self.target(connection, False)
        self.target(connection, False) # FIXME duplicate
