import pyBallLib

serial_port = 'COM3'
zone_serial = '1026CCE9FBFDFBD8'
zone_channel = 0
device_serials = [
    '241EC4C1CED2CDEF',
    '271FC4C0CDD0CDEE'
]

connection = pyBallLib.Connection(serial_port)
zone = pyBallLib.Zone(connection, zone_serial, zone_channel)

# Assign each device to the zone
for device_serial in device_serials:
    print("Assigning {device_serial} to {zone_serial}:{zone_channel}".format(
        device_serial=device_serial,
        zone_serial=zone_serial,
        zone_channel=zone_channel,
    ))
    zone.assign_device(device_serial)

# Force a time update
zone.set_time()
