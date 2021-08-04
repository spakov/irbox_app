from enum import Enum, unique

@unique
class Protocol(Enum):
    """
    Arduino-IRremote protocols. Adapted from src/IRProtocol.h commit
    39eec4c5caa4e7f2ba94003d2fe0e83d9c2b29a5.
    """

    UNKNOWN = 0
    PULSE_DISTANCE = 1
    PULSE_WIDTH = 2
    DENON = 3
    DISH = 4
    JVC = 5
    LG = 6
    LG2 = 7
    NEC = 8
    PANASONIC = 9
    KASEIKYO = 10
    KASEIKYO_JVC = 11
    KASEIKYO_DENON = 12
    KASEIKYO_SHARP = 13
    KASEIKYO_MITSUBISHI = 14
    RC5 = 15
    RC6 = 16
    SAMSUNG = 17
    SHARP = 18
    SONY = 19
    ONKYO = 20
    APPLE = 21
    BOSEWAVE = 22
    LEGO_PF = 23
    MAGIQUEST = 24
    WHYNTER = 25
