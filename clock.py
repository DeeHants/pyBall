import datetime
import math
import time

import pyBallLib

serial_port = 'COM3'
zone_serial = '1026CCE9FBFDFBD8'
zone_channel = 0

# Create the zone and sequence
connection = pyBallLib.Connection(serial_port)
zone = pyBallLib.Zone(connection, zone_serial, zone_channel)
sequence = zone.bank(0).sequence(0)


def degree_position(degrees, length):
    # Convert to radians
    radians = degrees * (3.14159 / 180)

    # X/Y (-1 to 1, around 0)
    s = math.sin(radians)
    c = math.cos(radians)

    # Adjust for the image size and centre offset
    x = int((s * length) + 36)
    y = int((c * length) + 36)

    return (x, y)


# Create a blank 73x73 image
image = sequence.append_image(73)

# Create the colour tuples
COLOUR_WHITE = (1, 1, 1)
COLOUR_BLACK = (0, 0, 0)
COLOUR_RED = (1, 0, 0)
COLOUR_GREEN = (0, 1, 0)
COLOUR_BLUE = (0, 0, 1)

# Draw the clock face
image.set_pixel(36, 36, COLOUR_WHITE)  # Center
for degree in range(360):
    coords = degree_position(degree, 36)
    image.set_pixel(coords[0], coords[1], COLOUR_WHITE)  # Outer circle
for degree in range(0, 360, 30):
    coords = degree_position(degree, 34)
    image.set_pixel(coords[0], coords[1], COLOUR_WHITE)  # Hour marks

# Calculate the gaps between the faces
faces = 4
gap = 10
terminus = min(gap, 10)  # Allow for the start/end gap

# Setup the sequence
position = sequence.append_position()  # Create B0S0P0
position.image = image.index
position.columns = ((image.width + gap) * faces) - terminus
position.gap = gap

# Upload the data
zone.upload()

# Allow it to restart
time.sleep(10)
zone.target(True)

second_coords = None
minute_coords = None
hour_coords = None
while True:
    # Update for the current time
    now = datetime.datetime.now()

    # Keep an array of update columns
    changed_columns = []

    # Second hand
    second = now.second
    new_second_coords = degree_position(second * 6, 30)
    if (second_coords != new_second_coords):
        # If it changed...
        if second_coords != None:
            # Clear old pixel
            image.set_pixel(second_coords[0], second_coords[1], COLOUR_BLACK)  # Off
            if second_coords[0] not in changed_columns:
                changed_columns.append(second_coords[0])
        # Set new pixel
        image.set_pixel(new_second_coords[0], new_second_coords[1], COLOUR_RED)  # Red
        if new_second_coords[0] not in changed_columns:
            changed_columns.append(new_second_coords[0])
        second_coords = new_second_coords

    # Minute hand
    minute = now.minute + (second / 60.0)  # Force to float
    new_minute_coords = degree_position(minute * 6, 25)
    if (minute_coords != new_minute_coords):
        # If it changed...
        if minute_coords != None:
            # Clear old pixel
            image.set_pixel(minute_coords[0], minute_coords[1], COLOUR_BLACK)  # Off
            if minute_coords[0] not in changed_columns:
                changed_columns.append(minute_coords[0])
        # Set new pixel
        image.set_pixel(new_minute_coords[0], new_minute_coords[1], COLOUR_GREEN)  # Green
        if new_minute_coords[0] not in changed_columns:
            changed_columns.append(new_minute_coords[0])
        minute_coords = new_minute_coords

    # Hour hand
    hour = now.hour + (minute / 60.0)  # Force to float
    new_hour_coords = degree_position(hour * 30, 20)
    if (hour_coords != new_hour_coords):
        # If it changed...
        if hour_coords != None:
            # Clear old pixel
            image.set_pixel(hour_coords[0], hour_coords[1], COLOUR_BLACK)  # Off
            if hour_coords[0] not in changed_columns:
                changed_columns.append(hour_coords[0])
        # Set new pixel
        image.set_pixel(new_hour_coords[0], new_hour_coords[1], COLOUR_BLUE)  # Blue
        if new_hour_coords[0] not in changed_columns:
            changed_columns.append(new_hour_coords[0])
        hour_coords = new_hour_coords

    # Update any changed columns
    for col in changed_columns:
        image.upload_col(col)

    # Re-upload the entire image
    # image.upload(image.offset)

    # Sleep 500ms
    time.sleep(1)
