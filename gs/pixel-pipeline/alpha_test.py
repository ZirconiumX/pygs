from enum import IntEnum
from nmigen import Elaboratable, Signal, Module
from nmigen.back import rtlil, verilog

from common import PixelFormat

class AlphaTestMode(IntEnum):
    NEVER    = 0    # All pixels fail
    ALWAYS   = 1    # All pixels pass
    LESS     = 2    # Pixels with alpha less than AREF pass
    LEQUAL   = 3    # Pixels with alpha less than or equal to AREF pass
    EQUAL    = 4    # You get the idea
    GEQUAL   = 5
    GREATER  = 6
    NOTEQUAL = 7


class AlphaFailMode(IntEnum):
    KEEP     = 0   # Neither the framebuffer nor the Z buffer are updated
    FB_ONLY  = 1   # Only the framebuffer is updated
    ZB_ONLY  = 2   # Only the Z buffer is updated
    RGB_ONLY = 3   # Only the framebuffer is updated, but alpha is not modified


class AlphaTest(Elaboratable):
    def __init__(self):
        self.i_rgbrndr = Signal()   # Whether to render this pixel's RGB; Off or On
        self.i_arndr   = Signal()   # Whether to render this pixel's Alpha; Off or On
        self.i_zrndr   = Signal()   # Whether to update this pixel's Z; Off or On

        self.i_enable  = Signal()   # Enable; Off or On
        self.i_test    = Signal(3)  # Which test to use; see AlphaTestMode
        self.i_failmod = Signal(2)  # Behaviour on test failure; see AlphaFailMode
        self.i_aref    = Signal(8)  # Q8.0; Reference Alpha Value

        self.i_x_coord = Signal(16) # Q12.4; Pixel X Coordinate
        self.i_y_coord = Signal(16) # Q12.4; Pixel Y Coordinate
        self.i_z_coord = Signal(32) # Float32; Pixel Z Coordinate

        self.i_red     = Signal(8)  # Q8.0; Pixel Red Channel
        self.i_green   = Signal(8)  # Q8.0; Pixel Green Channel
        self.i_blue    = Signal(8)  # Q8.0; Pixel Blue Channel
        self.i_alpha   = Signal(8)  # Q8.0; Pixel Alpha (Transparency) Channel

        self.i_fbpxfmt = Signal(6)  # Framebuffer Pixel Format

        self.o_rgbrndr = Signal()   # Whether to render this pixel's RGB; Off or On
        self.o_arndr   = Signal()   # Whether to render this pixel's Alpha; Off or On
        self.o_zrndr   = Signal()   # Whether to update this pixel's Z; Off or On

        self.o_x_coord = Signal(16) # Output X Coordinate
        self.o_y_coord = Signal(16) # Output Y Coordinate
        self.o_z_coord = Signal(32) # Output Z Coordinate

        self.o_red     = Signal(8)  # Output Red Channel
        self.o_green   = Signal(8)  # Output Green Channel
        self.o_blue    = Signal(8)  # Output Blue Channel
        self.o_alpha   = Signal(8)  # Output Alpha Channel

    def elaborate(self, platform):
        m = Module()

        # Move the pipeline along
        m.d.sync += [
            self.o_x_coord.eq(self.i_x_coord),
            self.o_y_coord.eq(self.i_y_coord),
            self.o_z_coord.eq(self.i_z_coord),

            self.o_red.eq(self.i_red),
            self.o_green.eq(self.i_green),
            self.o_blue.eq(self.i_blue),
            self.o_alpha.eq(self.i_alpha)
        ]

        # Alpha Test, relative to AREF.
        test = Signal()

        with m.If(self.i_enable):
            with m.Switch(self.i_test):
                with m.Case(AlphaTestMode.NEVER):
                    m.d.comb += test.eq(0)
                with m.Case(AlphaTestMode.ALWAYS):
                    m.d.comb += test.eq(1)
                with m.Case(AlphaTestMode.LESS):
                    m.d.comb += test.eq(self.i_alpha < self.i_aref)
                with m.Case(AlphaTestMode.LEQUAL):
                    m.d.comb += test.eq(self.i_alpha <= self.i_aref)
                with m.Case(AlphaTestMode.EQUAL):
                    m.d.comb += test.eq(self.i_alpha == self.i_aref)
                with m.Case(AlphaTestMode.GEQUAL):
                    m.d.comb += test.eq(self.i_alpha >= self.i_aref)
                with m.Case(AlphaTestMode.GREATER):
                    m.d.comb += test.eq(self.i_alpha > self.i_aref)
                with m.Case(AlphaTestMode.NOTEQUAL):
                    m.d.comb += test.eq(self.i_alpha != self.i_aref)
        with m.Else():
            m.d.comb += test.eq(1)

        with m.Switch(self.i_failmod):
            with m.Case(AlphaFailMode.KEEP):
                m.d.sync += [
                    self.o_rgbrndr.eq(self.i_rgbrndr & test),
                    self.o_arndr.eq(self.i_arndr & test),
                    self.o_zrndr.eq(self.i_zrndr & test)
                ]
            with m.Case(AlphaFailMode.FB_ONLY):
                m.d.sync += [
                    self.o_rgbrndr.eq(self.i_rgbrndr),
                    self.o_arndr.eq(self.i_arndr),
                    self.o_zrndr.eq(self.i_zrndr & test)
                ]
            with m.Case(AlphaFailMode.ZB_ONLY):
                m.d.sync += [
                    self.o_rgbrndr.eq(self.i_rgbrndr & test),
                    self.o_arndr.eq(self.i_arndr & test),
                    self.o_zrndr.eq(self.i_zrndr)
                ]
            with m.Case(AlphaFailMode.RGB_ONLY):
                # "RGB_ONLY is effective only when the color format is RGBA32.
                # In other formats, operation is made with FB_ONLY." - GS User's Manual
                with m.If(self.i_fbpxfmt == PixelFormat.PSMCT32):
                    m.d.sync += [
                        self.o_rgbrndr.eq(self.i_rgbrndr),
                        self.o_arndr.eq(self.i_arndr & test),
                        self.o_zrndr.eq(self.i_zrndr & test)
                    ]
                with m.Else():
                    m.d.sync += [
                        self.o_rgbrndr.eq(self.i_rgbrndr),
                        self.o_arndr.eq(self.i_arndr),
                        self.o_zrndr.eq(self.i_zrndr & test)
                    ]

        return m

if __name__ == "__main__":
    atst = AlphaTest()

    ports = [
        atst.i_enable, atst.i_test, atst.i_aref,

        atst.i_rgbrndr, atst.i_arndr, atst.i_zrndr,
        atst.i_x_coord, atst.i_y_coord, atst.i_z_coord,
        atst.i_red, atst.i_green, atst.i_blue, atst.i_alpha,
        atst.i_fbpxfmt,

        atst.o_rgbrndr, atst.o_arndr, atst.o_zrndr,
        atst.o_x_coord, atst.o_y_coord, atst.o_z_coord,
        atst.o_red, atst.o_green, atst.o_blue, atst.o_alpha,
    ]

    print(verilog.convert(atst, ports=ports))
