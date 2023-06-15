__copyright__ = "Copyright Earl Software"
__license__ = "This source code is subject to the BSD 3-Clause license. See Licence.txt for the full licence."
__author__ = "Deanna Earley"

# iBall op values
class Ops:
    TARGET_DEVICE = 0x00
    TARGET_ZONE = 0x01
    STORE = 0x02
    SETTIME = 0x04
    X7 = 0x07
    X8 = 0x08
    REINIT = 0xFF


class Addr:
    ZERO = 0x0000
    POSITION_BASE = 0x2100
    IMAGE_BASE = 0x3100
    DATA_BASE = 0x3500
