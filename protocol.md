# Opti-space/SpaceWriter communications protocol #

This document describes the serial protocol used to programme and control the SpaceWriter/Opti-space range of display/advertising devices including the iBall, FanScreen, SignLine and WallScreen.

**Note, this is unofficial documentation, derived from monitoring communication with the device, with no access to the original source code or documentation. Some details may not be 100% correct.**

Collated by Deanna Earley, dee@earlsoft.co.uk.

## Protocol ##

Communication is over a serial link, at 38400 baud with 8N1 line control.

Devices are "programmed" with a software serial number and channel, which is used for all other communication once set.
Multiples devices can share a serial and channel, and be programmed simultaneously with the serial passthru or splitting.
For brevity, the rest of this document will assume a single device.

All commands are sent as single "packets" of data, made up of a single byte, followed by a number of 16-bit words in little-endian, the last of which is is a checksum.

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

The Target operation specifies the software serial number and channel of all devices that should receive the subsequent commands.

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
This covers the vast majority of programming of the devices and includes the device state, repeat values, position settings, image and font data, etc.

     02 08 01 00 00 04 00 00 00 00 00 00 00 06 04 14 05
     02 0D 01 00 00 01 00 00 00                   10 01
    |Op|Addr1|Addr2|Len  |Payload                |Sum  |

* Operation: `0x02`
* Address 1: Start memory address to write to
* Address 2: Bank/sequence address
* Length: The number of words to store from the start address
* Payload: The data to store from Start to Start + Length - 1

Bank/sequence is `0x0000` in most cases, but for bank and sequence data, extends the address space up to 64x, 4 banks of 16 sequences.
All device settings are set on the first bank and sequence (`0x0000`).

### Re-initialise, 0xFF ###

The Re-initalise operation causes the device to restart and reread any stored data.

     FF 00 00 00 00 01 00 01 00 01 01
    |Op|Addr1|Addr2|Len  |     |Sum  |

* Operation: `0xff`
* Address 1: `0x0000`
* Address 2: `0x0000`
* Payload: `0x0001`
