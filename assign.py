import pyBallLib

serial_port = 'COM3'
zone_serial = '1026CCE9FBFDFBD8'
zone_channel = 0
device_serials = [
    '241EC4C1CED2CDEF',
    '271FC4C0CDD0CDEE'
]

connection = pyBallLib.Connection(serial_port)

# Part of the assignation needs the zone serial as individual bytes
zone_serial_bytes = []
for offset in [14, 12, 10, 8, 6, 4, 2, 0]:
    zone_serial_bytes.append(int(zone_serial[offset:offset + 2], 16))

# Not talking to anything
connection.target_zone(zone_serial, zone_channel, False)

for device_serial in device_serials:
    print 'Assigning ' + device_serial + ' to ' + zone_serial + ':' + str(zone_channel)

    # Select the device we're talking to
    connection.target_device(device_serial, True)

    # Register this device with the zone serial and channel
    connection.send(pyBallLib.Ops.STORE, 0x010C, 0x0000, 0)
    connection.send(pyBallLib.Ops.STORE, 0x0100, 0x0000, [zone_serial, zone_channel])
    connection.send(pyBallLib.Ops.STORE, 0x0000, 0x4001, zone_serial_bytes + [zone_channel, 2])

    # Re-initialise
    connection.send(pyBallLib.Ops.REINIT, 0x0000, 0x0000, 1)

# Not talking to anything again
connection.target_zone(zone_serial, zone_channel, False)
