from nmigen import Elaboratable, Module, Signal


class Dither(Elaboratable):
    def __init__(self):
        self.i_enable = Signal()    # Whether to perform dithering

        self.i_dm00   = Signal((3, True))  # (0, 0) dither matrix
        self.i_dm01   = Signal((3, True))  # (1, 0) dither matrix
        self.i_dm02   = Signal((3, True))  # (2, 0) dither matrix
        self.i_dm03   = Signal((3, True))  # (3, 0) dither matrix
        self.i_dm10   = Signal((3, True))  # (0, 1) dither matrix
        self.i_dm11   = Signal((3, True))  # (1, 1) dither matrix
        self.i_dm12   = Signal((3, True))  # (2, 1) dither matrix
        self.i_dm13   = Signal((3, True))  # (3, 1) dither matrix
        self.i_dm20   = Signal((3, True))  # (0, 2) dither matrix
        self.i_dm21   = Signal((3, True))  # (1, 2) dither matrix
        self.i_dm22   = Signal((3, True))  # (2, 2) dither matrix
        self.i_dm23   = Signal((3, True))  # (3, 2) dither matrix
        self.i_dm30   = Signal((3, True))  # (0, 3) dither matrix
        self.i_dm31   = Signal((3, True))  # (1, 3) dither matrix
        self.i_dm32   = Signal((3, True))  # (2, 3) dither matrix
        self.i_dm33   = Signal((3, True))  # (3, 3) dither matrix

        self.i_rgbrndr = Signal()   # Whether to render this pixel's RGB; Off or On
        self.i_arndr   = Signal()   # Whether to render this pixel's Alpha; Off or On
        self.i_zrndr   = Signal()   # Whether to update this pixel's Z; Off or On

        self.i_x_coord = Signal(16) # Q12.4; Pixel X Coordinate
        self.i_y_coord = Signal(16) # Q12.4; Pixel Y Coordinate
        self.i_z_coord = Signal(32) # Float32; Pixel Z Coordinate

        self.i_red     = Signal(9)  # Q9.0; Pixel Red Channel
        self.i_green   = Signal(9)  # Q9.0; Pixel Green Channel
        self.i_blue    = Signal(9)  # Q9.0; Pixel Blue Channel
        self.i_alpha   = Signal(8)  # Q9.0; Pixel Alpha (Transparency) Channel

        self.i_fbpxfmt = Signal(6)  # Framebuffer Pixel Format
        self.i_zbfmt   = Signal(6)  # Z Buffer Format

        self.o_rgbrndr = Signal()   # Whether to render this pixel's RGB; Off or On
        self.o_arndr   = Signal()   # Whether to render this pixel's Alpha; Off or On
        self.o_zrndr   = Signal()   # Whether to update this pixel's Z; Off or On

        self.o_x_coord = Signal(16) # Output X Coordinate
        self.o_y_coord = Signal(16) # Output Y Coordinate
        self.o_z_coord = Signal(32) # Output Z Coordinate

        self.o_red     = Signal(9)  # Output Red Channel
        self.o_green   = Signal(9)  # Output Green Channel
        self.o_blue    = Signal(9)  # Output Blue Channel
        self.o_alpha   = Signal(8)  # Output Alpha Channel

    def _dither(self, m, dither0, dither1, dither2, dither3):
        with m.Switch(self.i_x_coord & 3):
            with m.Case(0):
                m.d.sync += [
                    self.o_red.eq(self.i_red + dither0),
                    self.o_green.eq(self.i_green + dither0),
                    self.o_blue.eq(self.i_blue + dither0)
                ]
            with m.Case(1):
                m.d.sync += [
                    self.o_red.eq(self.i_red + dither1),
                    self.o_green.eq(self.i_green + dither1),
                    self.o_blue.eq(self.i_blue + dither1)
                ]
            with m.Case(2):
                m.d.sync += [
                    self.o_red.eq(self.i_red + dither2),
                    self.o_green.eq(self.i_green + dither2),
                    self.o_blue.eq(self.i_blue + dither2)
                ]
            with m.Case(3):
                m.d.sync += [
                    self.o_red.eq(self.i_red + dither3),
                    self.o_green.eq(self.i_green + dither3),
                    self.o_blue.eq(self.i_blue + dither3)
                ]

    def elaborate(self, platform):
        m = Module()

        # Move the pipeline along
        m.d.sync += [
            self.o_rgbrndr.eq(self.i_rgbrndr),
            self.o_arndr.eq(self.i_arndr),
            self.o_zrndr.eq(self.i_zrndr),

            self.o_x_coord.eq(self.i_x_coord),
            self.o_y_coord.eq(self.i_y_coord),
            self.o_z_coord.eq(self.i_z_coord),

            self.o_alpha.eq(self.i_alpha),
        ]        

        with m.Switch(self.i_y_coord & 3):
            with m.Case(0):
                self._dither(m, self.i_dm00, self.i_dm01, self.i_dm02, self.i_dm03)
            with m.Case(1):
                self._dither(m, self.i_dm10, self.i_dm11, self.i_dm12, self.i_dm13)
            with m.Case(2):
                self._dither(m, self.i_dm20, self.i_dm21, self.i_dm22, self.i_dm23)
            with m.Case(3):
                self._dither(m, self.i_dm30, self.i_dm31, self.i_dm32, self.i_dm33)

        return m
