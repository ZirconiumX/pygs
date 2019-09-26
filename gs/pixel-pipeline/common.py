from enum import IntEnum


class PixelFormat(IntEnum):
    # RGBA framebuffer formats
    PSMCT32  = 0  # R8 G8 B8 A8
    PSMCT24  = 1  # R8 G8 B8
    PSMCT16  = 2  # R5 G5 B5 A1
    PSMCT16S = 10 # R5 G5 B5 A1

    PSMZ32   = 48 # Z32
    PSMZ24   = 49 # Z24
    PSMZ16   = 50 # Z16
    PSMZ16S  = 58 # Z16
