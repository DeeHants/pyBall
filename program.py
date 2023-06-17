import pyBallLib

serial_port = 'COM3'
zone_serial = '1026CCE9FBFDFBD8'
zone_channel = 0

# Create the zone
connection = pyBallLib.Connection(serial_port)
zone = pyBallLib.Zone(connection, zone_serial, zone_channel)

# First sequence
sequence = zone.bank(0).sequence(0)

# B0S0P0 black mouse clockwise
image = sequence.append_image(100, image_filename='mouseb.pbi')
position = sequence.append_position()  # Create B0S0P0
position.image = image.index
position.columns = 355
position.gap = 255
position.scroll = 2  # LTR
position.frames = 500

# B0S0P1 red mouse anti-clockwise
image = sequence.append_image(100, image_filename='mouser.pbi')
position = sequence.append_position()  # Create B0S0P1
position.image = image.index
position.columns = 355
position.gap = 255
position.scroll = 353  # RTL
position.frames = 500

# Second sequence
sequence = zone.bank(1).sequence(1)
sequence.repeat = 10

# B0S0P0 black mouse clockwise
image = sequence.append_image(100, image_filename='mouseb.pbi')
position = sequence.append_position()  # Create B1S1P0
position.image = image.index
position.columns = 300
position.gap = 0
position.scroll = 0
position.frames = 10

# B0S0P1 red mouse anti-clockwise
image = sequence.append_image(100, image_filename='mouser.pbi')
position = sequence.append_position()  # Create B1S1P1
position.image = image.index
position.columns = 300
position.gap = 0
position.scroll = 0
position.frames = 10

# Upload the data
zone.updatestate()
zone.upload()
