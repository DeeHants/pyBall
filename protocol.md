# Opti-space/SpaceWriter communications protocol #

This document describes the serial protocol used to programme and control the SpaceWriter/Opti-space range of display/advertising devices including the iBall, FanScreen, SignLine and WallScreen.

**Note, this is unofficial documentation, derived from monitoring communication with the device, with no access to the original source code or documentation. Some details may not be 100% correct.**

Collated by Deanna Earley, dee@earlsoft.co.uk.

## Protocol ##

Communication is over a serial link, at 38400 baud with 8N1 line control.

Devices are "programmed" with a software serial number and channel, which is used for all other communication once set.
Multiples devices can share a serial and channel, and be programmed simultaneously with the serial passthru or splitting.
For brevity, the rest of this document will assume a single device.

All commands are sent as single "packets" of data, made up of a single byte, followed by a number of 16-bit words in little endian, the last of which is a checksum.

     02 08 01 00 00 04 00 00 00 00 00 01 00 00 04 0F 05
    |Op|Addr1|Addr2|Len  |Payload                |Sum  |

* Operation: A single byte signifying the operation/command
* Address 1: Primary memory address
* Address 2: Secondary memory address
* Length: Number of 16-bit words in the payload
* Payload: Command payload, 2 x len bytes long
* Checksum: Arithmetic sum of the 16-bit values

The checksum is a simple arithmetic sum of the operation byte, and each 16-bit word, modular divided by `0xffff`:

    sum = (op + addr1 + addr2 + len + payload[0] .. payload[n]) mod 0xffff

## Operations ##

### Target device, `0x00` ###

The Target device operation specifies the serial number of the device that should listen to the subsequent packets.

* Operation: `0x00`
* Address 1: `0x0000`
* Address 2: `0x0000`
* Length: 5
* Payload

       EF CD D2 CE C1 C4 1E 24 01 00
       EF CD D2 CE C1 C4 1E 24 00 00
      |Software serial        |Mode |

  * Device serial: The serial is handled slightly differently in that the entire 8 bytes is sent, little endian over 4 words. The example represents `241E C4C1 CED2 CDEF`
  * Mode: Set to `0x0001` when sending commands, and `0x0000` at the end.

### Target zone, `0x01` ###

The Target zone operation specifies the software serial number and channel of the device that should listen to the subsequent packets.

* Operation: `0x01`
* Address 1: `0x0000`
* Address 2: `0x0000`
* Length: 6
* Payload

       D8 FB FD FB E9 CC 26 10 00 00 01 00
       D8 FB FD FB E9 CC 26 10 00 00 00 00
       D8 FB FD FB E9 CC 26 10 01 00 01 00
       D8 FB FD FB E9 CC 26 10 01 00 00 00
      |Software serial        |Chan |Mode |

  * Software serial: The serial is handled slightly differently in that the entire 8 bytes is sent, little endian over 4 words. The example represents `1026 CCE9 FBFD FBD8`
  * Channel: The 0 based channel number
  * Mode: Set to `0x0001` when sending commands, and `0x0000` at the end.

### Store, `0x02` ###

The Store operation writes a block of data to a memory location on the device.
This covers the vast majority of programming of the device and includes the device state, repeat values, position settings, image and font data, etc.

     02 08 01 00 00 04 00 00 00 00 00 00 00 06 04 14 05
     02 0D 01 00 00 01 00 00 00                   10 01
    |Op|Addr1|Addr2|Len  |Payload                |Sum  |

* Operation: `0x02`
* Address 1: Start memory address to write to
* Address 2: Bank/sequence address
* Length: The number of words to store from the start address
* Payload: The data to store from Start to Start + Length - 1

Bank/sequence address is `0x0000` in most cases, but for bank and sequence data, extends the address space up to 64x, to allow 4 banks of 16 sequences.
All device settings are set on the first bank and sequence (`0x0000`).

### Set date/time, `0x04` ###

The date and time operation sets the current date, time, and weekday on the device, used for scheduling.

     04  BE 00  00 00  04 00  39 41 12 26 01 01 20 80  32 E9
     04  BE 00  00 00  04 00  11 03 13 24 10 07 20 80  1A AF
    |op |      |      |len   |se|mi|ho|da|mo|wd|yr|   |sum  |

* Operation: `0x04`
* Address 1: `0x00BE`
* Address 2: `0x0000`
* Length: 4
* Payload

       39 41 12 26 01 01 20 80 # 26/01/2020 12:41:39
       11 03 13 24 10 07 20 80 # 24/10/2020 13:03:11
      |se|mi|ho|da|mo|wd|yr|  |

  * Seconds, Minutes, Hour: Time components
  * Day, Month: Date components
  * Weekday: 1, Sunday - 7, Saturday
  * Year: Years from 2000. 2020 = 20, 1991 = -9

Each of the payload components are packed into each value using [simple binary encoded decimal](https://en.wikipedia.org/wiki/Binary-coded_decimal).  
This means a value of 19 is `0x19`, 20 is `0x20`.  
Negative values are complement based value, with a radix of 13 for the units, and 5 for the tens.

### Enable display, `0x07` ###

This operation enables or disables the display output. Animation and sequencing will carry on if the output is disabled.

     07 00 00 00 00 01 00 01 00 09 00
    |Op|Addr1|Addr2|Len  |     |Sum  |

* Operation: `0x07`
* Address 1: `0x0000`
* Address 2: `0x0000`
* Payload: `0x0001` for output, `0x0000` for no output

### Re-initialise, `0xff` ###

The Re-initalise operation causes the device to restart and reread any stored data.

     FF 00 00 00 00 01 00 01 00 01 01
    |Op|Addr1|Addr2|Len  |     |Sum  |

* Operation: `0xff`
* Address 1: `0x0000`
* Address 2: `0x0000`
* Payload: `0x0001`

## Memory addresses ##

Every setting or value is stored at a particular address, with the entire address space split into several ranges.
Values can either be set individually, or in a block for a set of sequential values.

Many of these addresses are specified with the bank/sequence in address 2.
This is composed of the sequence index (0 based) in the low nibble, an the bank index (0 based) in the high nibble of the first byte, e.g. Bank 2, sequence 5 will be `0x0014`.

* `0x0100-0x01ff`: Device wide data
* `0x0200-0x11ff`: Schedule data
* `0x2000-0x20ff`: Sequence data
* `0x2100-0x30ff`: Position data
* `0x3100-0xffff`: Image pool data

### Device values ###

Device wide data is stored in addresses in the range `0x0100-0x1fff`.
All these values have `0x0000` in address 2.

* `0x0100-0x0103`: Software serial 8 bytes, little endian
* `0x0104`: Channel number, 0 to 255
* `0x0108`: Active position, 0 to n
* `0x0109`: Active sequence, 0 to 15
* `0x010a`: Active bank, 0 to 3
* `0x010b`: Chase state
  * low byte, bit 0: Freeze/don't chase positions
  * low byte, bit 1: Don't chase sequences
  * low byte, bit 2: Don't chase banks
  * high byte: Maximum bank to chase (1 based)
* `0x010d`: Scheduler enabled
* `0x0180`: Bank 1 additional repeat count <sup>1</sup>
* `0x0181`: Bank 2 additional repeat count <sup>1</sup>
* `0x0182`: Bank 3 additional repeat count <sup>1</sup>
* `0x0183`: Bank 4 additional repeat count <sup>1</sup>

<sup>1</sup> Repeat counts are 0 based, 0 = repeat once, 1 = repeat twice, etc).

## Schedule ###

Schedule data is stored in addresses in the range `0x0200-0x11ff`.
These make use of the bank/sequence address in address 2 to increase the number of allowable entries.
Address `0x01ff` is used to store the index/address of the maximum expected schedule entry.

Each schedule entry is defined in blocks of 4 values, repeated 65534 times in sequential blocks.

* `0x0200`: Month (high byte) and day (low byte)
* `0x0201`: Hour (high byte) and minute (low byte)
* `0x0202`: Bank (low nibble of high byte) and sequence (low byte) to switch to, with other bits also set for other flags

These repeat 65534 times with the first at `0x0200, 0x0000`, second at `0x0204, 0x0000`, 250th at `0x11ff, 0x0000`, 251st in the next bank/sequences at `0x0200, 0x0100`, putting the last value at `0x11ff, 0x3f00`.

### Sequence values ###

Sequence data is stored in addresses in the range `0x2000-0x20ff`.
All these values use the bank/sequence address in address 2.

* `0x2000`: Sequence state
* `0x2001`: Sequence additional repeat count <sup>1</sup>
* `0x2002`: Number of valid positions
* `0x2003-0x2004`: Sequence checksum, sum of all words in the sequence image data and image metadata

<sup>1</sup> Repeat counts are 0 based, 0 = repeat once, 1 = repeat twice, etc).

### Position values ###

Position data is stored in addresses in the range `0x2100-0x30ff`.
Like the sequence values above, all these values use the bank/sequence address in address 2.

Each position is defined in blocks of 16 values, repeated 256 times in sequential blocks.

Most of these values are relative to the image width. Examples below will be based on a 100 pixels wide.

* `0x2100`: Image index
* `0x2101`: Columns, total width of the rendered image with gaps.
* `0x2102`: Gap size, gap between each image repeat
* `0x2103`: Brilliance, 0 to 255
* `0x2104`: Scroll speed, 0 is stationary, 1 to half the width scrolls to the left, above half scrolls to the right
* `0x2105`: Rotational position offset
* `0x2106`: Repeat index of the position to repeat from
* `0x2107`: Repeat count <sup>1</sup>
* `0x2109`: Flash Interval & wipe increment
  * low byte: Number of frame between flashing on and off. 0 to 128, higher numbers are slower.
  * high byte: Wipe increment, the number of columns to reveal each frame. 0 to 127, higher numbers are quicker.
* `0x210a`: Fade in/out increment (first byte is in, second is out)
  * low byte: Fade in increment of the brilliance, 0 to 127, higher numbers are quicker.
  * high byte: Fade out decrement of the brilliance. 0 to 127, higher numbers are quicker.
* `0x210f`: Number of frames before moving to the next position, or repeating.

These repeat 256 times with the first at `0x2100`, second at `0x2110`, and the last at `0x30f0`, putting the last value at `0x30ff`.

<sup>1</sup> Repeat counts are 0 based, 0 = repeat once, 1 = repeat twice, etc).

The iBall can show about 850 columns round. Having a 100 pixel image, with a columns of 800, will repeat the image 8 times.
Setting the gap to 300, would render at the same size, but only 2 of them on opposite sides (0-100 is image, 100-400 is gap, 400-500 is image, 500-800 is gap).
Setting the columns to 100 would stretch the image around the entire display.

The rotational position sets an offset in columns from the origin, and the scroll adjusts how many columns will be offset each frame.

### Image pool ###

Image pool data is stored in addresses in the range `0x3100-0xffff`.
Like the sequence values above, all these values use the bank/sequence address in address 2.

Each image pool entry is defined in blocks of 4 values, repeated 256 times in sequential blocks.

* `0x3100`: Image width (in pixels)
* `0x3102`: Image address

These repeat 256 times with the first at `0x3100`, second at `0x3104`, and the last at `0x34fc`, putting the last value at `0x34ff`.

The image data itself is written sequentially starting at address `0x3500`, with each block of 16 values representing the bitmap data of a single vertical line of an image.

* `0x3500-0xffff`: Image data
