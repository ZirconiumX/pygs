from enum import IntEnum
from nmigen import Elaboratable, Signal, Module
from nmigen.back import rtlil, verilog


class ClampingType(IntEnum):
    MASK  = 0 # Lower 8 bits of colour channel are output
    CLAMP = 1 # Colour channel is clamped to a maximum of 255.


class Clamp(Elaboratable):
    def __init__(self):
        self.i_clamp   = Signal()   # Whether to saturate or mask colour channels.
        self.i_alphcor = Signal()   # Alpha correction value

        self.i_rgbrndr = Signal()   # Whether to render this pixel's RGB; Off or On
        self.i_arndr   = Signal()   # Whether to render this pixel's Alpha; Off or On
        self.i_zrndr   = Signal()   # Whether to update this pixel's Z; Off or On

        self.i_x_coord = Signal(16) # Q12.4; Pixel X Coordinate
        self.i_y_coord = Signal(16) # Q12.4; Pixel Y Coordinate
        self.i_z_coord = Signal(32) # Float32; Pixel Z Coordinate

        self.i_red     = Signal(9)  # Q9.0; Pixel Red Channel
        self.i_green   = Signal(9)  # Q9.0; Pixel Green Channel
        self.i_blue    = Signal(9)  # Q9.0; Pixel Blue Channel
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

    @staticmethod
    def _clamp(m, i, o):
        with m.If(i > 255):
            m.d.sync += o.eq(255)
        with m.Else():
            m.d.sync += o.eq(i)

    def elaborate(self, platform):
        m = Module()

        # Move the pipeline along
        m.d.sync += [
            self.o_rgbrndr.eq(self.i_rgbrndr),
            self.o_arndr.eq(self.i_arndr),
            self.o_zrndr.eq(self.o_zrndr),

            self.o_x_coord.eq(self.i_x_coord),
            self.o_y_coord.eq(self.i_y_coord),
            self.o_z_coord.eq(self.i_z_coord),
        ]

        # Colour clamping
        with m.If(self.i_clamp == ClampingType.CLAMP):
            self._clamp(m, self.i_red, self.o_red)
            self._clamp(m, self.i_green, self.o_green)
            self._clamp(m, self.i_blue, self.o_blue)
        with m.Else():
            m.d.sync += [
                self.o_red.eq(self.i_red[0:7]),
                self.o_green.eq(self.i_green[0:7]),
                self.o_blue.eq(self.i_blue[0:7])
            ]

        # Alpha correction
        m.d.sync += self.o_alpha.eq(self.i_alpha | (self.i_alphcor << 7))

        return m

if __name__ == "__main__":
    clamp = Clamp()

    ports = [
        clamp.i_clamp, clamp.i_alphcor,

        clamp.i_rgbrndr, clamp.i_arndr, clamp.i_zrndr,
        clamp.i_x_coord, clamp.i_y_coord, clamp.i_z_coord,
        clamp.i_red, clamp.i_green, clamp.i_blue, clamp.i_alpha,

        clamp.o_rgbrndr, clamp.o_arndr, clamp.o_zrndr,
        clamp.o_x_coord, clamp.o_y_coord, clamp.o_z_coord,
        clamp.o_red, clamp.o_green, clamp.o_blue, clamp.o_alpha,
    ]

    print(verilog.convert(clamp, ports=ports))
