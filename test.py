import pyBallLib

# Create the zone
zone = pyBallLib.Zone()
zone.serial = '0123456789ABCDEF'

# First sequence
sequence = zone.bank(0).sequence(0)
for index in range(8, 10):
    sequence.images.append(pyBallLib.Image(sequence, index))

# B0S0P0 black mouse clockwise
position = sequence.append_position() # Create B0S0P0
position.image = 8
position.columns = 355
position.gap = 255
position.scroll = 2 # LTR
position.frames = 500

# B0S0P1 red mouse anti-clockwise
position = sequence.append_position() # Create B0S0P1
position.image = 9
position.columns = 355
position.gap = 255
position.scroll = 353 # RTL
position.frames = 500

# Second sequence
sequence = zone.bank(1).sequence(1)
sequence.repeat = 10
for index in range(8, 10):
    sequence.images.append(pyBallLib.Image(sequence, index))

# B0S0P0 black mouse clockwise
position = sequence.append_position() # Create B1S1P0
position.image = 8
position.columns = 300
position.gap = 0
position.scroll = 0
position.frames = 10

# B0S0P1 red mouse anti-clockwise
position = sequence.append_position() # Create B1S1P1
position.image = 9
position.columns = 300
position.gap = 0
position.scroll = 0
position.frames = 10

# Upload the data
connection = pyBallLib.Connection('COM3')
zone.upload(connection)
