from nmigen import Elaboratable, Signal, Module
from nmigen.back import rtlil

from common import PixelFormat


class DestinationAlphaTest(Elaboratable):
    def __init__(self):
        self.i_rgbrndr = Signal()   # Whether to render this pixel's RGB; Off or On
        self.i_arndr   = Signal()   # Whether to render this pixel's Alpha; Off or On
        self.i_zrndr   = Signal()   # Whether to update this pixel's Z; Off or On

        self.i_enable  = Signal()   # Enable; Off or On
        self.i_mode    = Signal()   # Alpha value to test for equality

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
            self.o_alpha.eq(self.i_alpha),
        ]

        # Destination Alpha Test, relative to MODE.
        test = Signal()

        # Test is skipped if there is no alpha coordinate in the buffer
        with m.If(self.i_enable & (self.i_fbpxfmt != PixelFormat.PSMCT24)):
            m.d.comb += test.eq(self.i_alpha[7] == self.i_mode)
        with m.Else():
            m.d.comb += test.eq(1)

        m.d.sync += [
            self.o_rgbrndr.eq(self.i_rgbrndr & test),
            self.o_arndr.eq(self.i_arndr & test),
            self.o_zrndr.eq(self.i_zrndr & test)
        ]

        return m

if __name__ == "__main__":
    atst = DestinationAlphaTest()

    ports = [
        atst.i_enable, atst.i_mode,

        atst.i_rgbrndr, atst.i_arndr, atst.i_zrndr,
        atst.i_x_coord, atst.i_y_coord, atst.i_z_coord,
        atst.i_red, atst.i_green, atst.i_blue, atst.i_alpha,
        atst.i_fbpxfmt,

        atst.o_rgbrndr, atst.o_arndr, atst.o_zrndr,
        atst.o_x_coord, atst.o_y_coord, atst.o_z_coord,
        atst.o_red, atst.o_green, atst.o_blue, atst.o_alpha,
    ]

    print(rtlil.convert(atst, ports=ports))
