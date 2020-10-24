import pyBallLib

serial_port = 'COM3'
zone_serial = '1026CCE9FBFDFBD8'
zone_channel = 0
device_serials = [
    '241EC4C1CED2CDEF',
    '271FC4C0CDD0CDEE'
]

connection = pyBallLib.Connection(serial_port)

# Not talking to anything
connection.target_zone(zone_serial, zone_channel, False)

zone = pyBallLib.Zone(zone_serial,zone_channel)
for device_serial in device_serials:
    print('Assigning ' + device_serial + ' to ' + zone_serial + ':' + str(zone_channel))
    zone.assigndevice(connection, device_serial)

# Not talking to anything again
connection.target_zone(zone_serial, zone_channel, False)
