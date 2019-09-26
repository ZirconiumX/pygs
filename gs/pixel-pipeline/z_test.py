from enum import IntEnum
from nmigen import Elaboratable, Signal, Module
from nmigen.back import rtlil


class ZTestMode(IntEnum):
    NEVER    = 0    # All pixels fail
    ALWAYS   = 1    # All pixels pass
    GEQUAL   = 2    # Pixels with a Z greater or equal to that of the Z buffer pass
    GREATER  = 3    # Pixels with a Z greater than the Z buffer pass


class ZTest(Elaboratable):
    def __init__(self):
        self.i_enable  = Signal()   # Enable; Off or On
                                    # Note that Z test disabled is marked as buggy, but we don't know why.
        self.i_test    = Signal(2)  # Which test to use; see ZTestMode
        self.i_zref    = Signal(32) # Reference Z Value

        self.i_rgbrndr = Signal()   # Whether to render this pixel's RGB; Off or On
        self.i_arndr   = Signal()   # Whether to render this pixel's Alpha; Off or On
        self.i_zrndr   = Signal()   # Whether to update this pixel's Z; Off or On

        self.i_x_coord = Signal(16) # Q12.4; Pixel X Coordinate
        self.i_y_coord = Signal(16) # Q12.4; Pixel Y Coordinate
        self.i_z_coord = Signal(32) # Float32; Pixel Z Coordinate

        self.i_red     = Signal(8)  # Q8.0; Pixel Red Channel
        self.i_green   = Signal(8)  # Q8.0; Pixel Green Channel
        self.i_blue    = Signal(8)  # Q8.0; Pixel Blue Channel
        self.i_alpha   = Signal(8)  # Q8.0; Pixel Alpha (Transparency) Channel

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

        # Z Test, relative to ZREF.
        test = Signal()
        with m.If(self.i_enable):
            with m.Switch(self.i_test):
                with m.Case(ZTestMode.NEVER):
                    m.d.comb += test.eq(0)
                with m.Case(ZTestMode.ALWAYS):
                    m.d.comb += test.eq(1)
                with m.Case(ZTestMode.GEQUAL):
                    m.d.comb += test.eq(self.i_z_coord >= self.i_zref)
                with m.Case(ZTestMode.GREATER):
                    m.d.comb += test.eq(self.i_z_coord > self.i_zref)
        with m.Else():
            m.d.comb += test.eq(1)

        m.d.sync += [
            self.o_rgbrndr.eq(self.i_rgbrndr & test),
            self.o_arndr.eq(self.i_arndr & test),
            self.o_zrndr.eq(self.i_zrndr & test)
        ]

        return m

if __name__ == "__main__":
    ztst = ZTest()

    ports = [
        ztst.i_enable, ztst.i_test, ztst.i_zref,

        ztst.i_rgbrndr, ztst.i_arndr, ztst.i_zrndr,
        ztst.i_x_coord, ztst.i_y_coord, ztst.i_z_coord,
        ztst.i_red, ztst.i_green, ztst.i_blue, ztst.i_alpha,

        ztst.o_rgbrndr, ztst.o_arndr, ztst.o_zrndr,
        ztst.o_x_coord, ztst.o_y_coord, ztst.o_z_coord,
        ztst.o_red, ztst.o_green, ztst.o_blue, ztst.o_alpha,
    ]

    print(rtlil.convert(ztst, ports=ports))
