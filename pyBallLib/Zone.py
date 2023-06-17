__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

import datetime

from .Constants import Ops, Addr
from .Bank import Bank


class Zone:
    def __init__(self, connection, serial='', channel=0):
        self._connection = connection
        self.name = ""
        self.serial = serial
        self.channel = channel

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

    def assigndevice(self, device_serial=''):
        # Not talking to anything
        self.target(False)

        # Part of the assignation needs the zone serial as individual bytes
        zone_serial_bytes = []
        for offset in [14, 12, 10, 8, 6, 4, 2, 0]:
            zone_serial_bytes.append(int(self.serial[offset:offset + 2], 16))

        print("Assigning {device_serial} to {zone_serial}:{zone_channel}".format(
            device_serial=device_serial,
            zone_serial=self.serial,
            zone_channel=self.channel,
        ))

        # Select the device we're talking to
        self._connection.target_device(device_serial, True)

        # Register this device with the zone serial and channel
        self._connection.send(
            Ops.STORE, 0x010C, 0x0000,  # FIXME what is addr 0x010C?
            0
        )
        self._connection.send(
            Ops.STORE, Addr.DEVICE_ZONE_SERIAL, 0x0000,  # and DEVICE_ZONE_CHANNEL
            [
                self.serial,
                self.channel
            ]
        )
        self._connection.send(
            Ops.STORE, 0x0000, 0x4001,
            zone_serial_bytes + [self.channel, 2]
        )

        # Re-initialise
        self._connection.send(Ops.REINIT, 0x0000, 0x0000, 1)

        # Not talking to anything again
        self.target(False)

    def updatestate(self):
        state = 0
        if self.freeze:
            state |= 0x01
        if not self.chase_sequences:
            state |= 0x02
        if not self.chase_banks:
            state |= 0x04
        state |= (self.chase_bank_max << 8)

        self._connection.send(
            Ops.X7,  0x0000, 0x0000,  # FIXME what is op 7?
            [1]
        )
        self._connection.send(
            Ops.STORE, Addr.DEVICE_ACTIVE_POSITION, 0x0000,  # and sequence, bank and state
            [
                self.active_position,
                self.active_sequence,
                self.active_bank,
                state
            ]
        )
        self._connection.send(
            Ops.STORE, Addr.DEVICE_SCHEDULE_ENABLED, 0x0000,
            [self.scheduler]
        )
        self._connection.send(
            Ops.X8, 0x0000, 0x0000,  # FIXME what is op 8?
            [1]
        )

    def bank(self, index):
        try:
            # Ensure we have an object
            if not self._banks[index]:
                self._banks[index] = Bank(self, index)

            # Return it
            return self._banks[index]

        except IndexError:
            # Re-raise IndexError with a more useful message
            raise IndexError("bank index out of range, must be 0-3")

    def target(self, enable):
        self._connection.target_zone(self.serial, self.channel, enable)

    def settime(self, time=0):
        def packed_bcd_value(value):
            # If it's negative, we need to use a complement value
            neg = value < 0
            if neg:
                value = abs(value) - 1

            # Each digit..
            units = value % 10
            tens = value // 10

            # If negative, get the complement value
            if neg:
                units = 13 - units
                tens = 5 - tens

            # Return the BCD value
            return tens << 4 | units

        # Use the current time if none was passed
        if time == 0:
            time = datetime.datetime.now()

        # Pack the date/time components into 4 16-bit words
        date_parts = [
            packed_bcd_value(time.second) |
            packed_bcd_value(time.minute) << 8,
            packed_bcd_value(time.hour) |
            packed_bcd_value(time.day) << 8,
            packed_bcd_value(time.month) |
            packed_bcd_value((time.isoweekday() % 7) + 1) << 8,
            packed_bcd_value(time.year - 2000) |
            0x8000
        ]

        self.target(True)
        self._connection.send(Ops.SETTIME, 0x00be, 0x0000, date_parts)
        self.target(False)

    def bs(self):
        return 0x0000

    def upload(self):
        if self.serial == '':
            raise Exception("zone serial has not been set")

        # Set the initial state
        print("Setting initial state")
        self.target(True)
        self.chase_banks = False
        self.chase_sequences = False
        self.updatestate()
        self._connection.send(
            Ops.STORE, 0x0106, 0x0000,  # FIXME what is addr 0x0106?
            [0]
        )
        self._connection.send(
            Ops.STORE, 0x0107, 0x0000,  # FIXME what is addr 0x0107?
            [0]
        )
        self._connection.send(
            Ops.STORE, 0x0105, 0x0000,  # FIXME what is addr 0x0105?
            [0]
        )
        # FIXME preserve state
        self.chase_banks = True
        self.chase_sequences = True
        self.updatestate()

        # Sync the time
        self.settime()

        self.target(True)  # FIXME is this no-op needed?
        self.target(False)

        # Upload each bank
        for bank in self._banks:
            if bank:
                bank.upload()

        # Set the final state
        self.target(True)
        self._connection.send(
            Ops.STORE, 0x0200, 0x0000,  # FIXME what is addr 0x0200?
            [
                0,
                0,
                0,
                0
            ]
        )
        self._connection.send(
            Ops.STORE, 0x01FF, 0x0000,  # FIXME what is addr 0x01ff?
            [0]
        )
        self._connection.send(
            Ops.STORE, 0x0180, 0x0000,  # FIXME what is addr 0x0180?
            [
                0,
                0,
                0,
                0
            ]
        )
        self.chase_banks = False
        self.chase_sequences = False
        self.updatestate()
        self.updatestate()  # FIXME 2nd time lucky?
        self.updatestate()  # FIXME 3rd time lucky?
        self._connection.send(Ops.REINIT, 0x0000, 0x0000, [1])  # Re-initialise
        self.target(False)
        self.target(False)  # FIXME duplicate
