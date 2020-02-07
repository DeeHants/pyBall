# Opti-space/SpaceWriter communications protocol #

This document describes the serial protocol used to programme and control the SpaceWriter/Opti-space range of display/advertising devices including the iBall, FanScreen, SignLine and WallScreen.

**Note, this is unofficial documentation, derived from monitoring communication with the device, with no access to the original source code or documentation. Some details may not be 100% correct.**

Collated by Deanna Earley, dee@earlsoft.co.uk.

## Protocol ##

Communication is over a serial link, at 38400 baud with 8N1 line control.

Devices are "programmed" with a software serial number and channel, which is used for all other communication once set.
Multiples devices can share a serial and channel, and be programmed simultaneously with the serial passthru or splitting.
For brevity, the rest of this document will assume a single device.

All commands are sent as single "packets" of data, made up of a single byte, followed by a number of 16-bit words in little-endian, the last of which is a checksum.

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

### Target, 0x01 ###

The Target operation specifies the software serial number and channel the device that should listen to the subsequent packets.

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

  * Software serial: The Software serial is handled slightly differently in that the entire 8 bytes is sent, little endian over 4 words. The example represents `1026 CCE9 FBFD FBD8`
  * Channel: The 0 based channel number
  * Mode: Set to `0x0001` when sending commands, and `0x0000` at the end.

### Store, 0x02 ###

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

### Re-initialise, 0xFF ###

The Re-initalise operation causes the device to restart and reread any stored data.

     FF 00 00 00 00 01 00 01 00 01 01
    |Op|Addr1|Addr2|Len  |     |Sum  |

* Operation: `0xff`
* Address 1: `0x0000`
* Address 2: `0x0000`
* Payload: `0x0001`

## Memory addresses ##

Every setting or value is stored at a particular address, with the entire range split into several ranges.
Values can either be set individually, or in a block for a set of sequential values.

Many of these addresses are specified with the bank/sequence in address 2.
This is composed of the sequence index (0 based) in the low nibble, an the bank index (0 based) in the high nibble of the first byte, e.g. Bank 2, sequence 5 will be `0x0014`.

### Device values ###

* `0x0100-0x0103`: Software serial 8 bytes, little endian
* `0x0104`: Channel number
* `0x0108`: Active position
* `0x0109`: Active sequence
* `0x010a`: Active bank
* `0x010b`: Chase state
* `0x010d`: Scheduler enabled
* `0x0180`: Bank 1 additional repeat count <sup>1</sup>
* `0x0181`: Bank 2 additional repeat count <sup>1</sup>
* `0x0182`: Bank 3 additional repeat count <sup>1</sup>
* `0x0183`: Bank 4 additional repeat count <sup>1</sup>

<sup>1</sup> Repeat counts are 0 based, 0 = repeat once, 1 = repeat twice, etc).

### Sequence values ###

All these values use the bank/sequence address in address 2.

* `0x2000`: Sequence state
* `0x2001`: Sequence additional repeat count <sup>1</sup>
* `0x2002`: Number of valid positions

<sup>1</sup> Repeat counts are 0 based, 0 = repeat once, 1 = repeat twice, etc).

### Position values ###

Like the sequence values above, all these values use the bank/sequence address in address 2.

Each position is defined in blocks of 16 values, repeated 256 times in sequential blocks.

* `0x2100`: Image index
* `0x2101`: Columns
* `0x2102`: Gap size
* `0x2103`: Brilliance
* `0x2104`: Scroll speed
* `0x2105`: Rotational position offset
* `0x2106`: Repeat index
* `0x2107`: Repeat count <sup>1</sup>
* `0x210f`: Frame count

These repeat 256 times with the first at `0x2100`, second at `0x2110`, and the last at `0x30f0`, putting the last value at `0x30ff`.

<sup>1</sup> Repeat counts are 0 based, 0 = repeat once, 1 = repeat twice, etc).

### Image pool ###

Like the sequence values above, all these values use the bank/sequence address in address 2.

Each image pool entry is defined in blocks of 4 values, repeated 256 times in sequential blocks.

* `0x3100`: Image width (in pixels)
* `0x3102`: Image address

These repeat 256 times with the first at `0x3100`, second at `0x3104`, and the last at `0x34fc`, putting the last value at `0x34ff`.

The image data itself is written starting at address `0x3500`, with each block of 16 values representing the bitmap data of a single vertical line of the image.

* `0x3500-0xffff`: Image data
