from nmigen import Cat, Const, Elaboratable, Memory, Module, Mux, Signal
from nmigen.back import pysim, rtlil, verilog


class ColourDivider(Elaboratable):
    def __init__(self):
        self.i_colour = Signal(16)
        self.i_dx     = Signal(16)
        self.i_start  = Signal()
        self.i_reset  = Signal()

        self.o_ready  = Signal()
        self.o_result = Signal(16)

        self.r_colour = Signal(16)
        self.r_recip  = Signal(16)

    def elaborate(self, platform):
        m = Module()

        with m.FSM() as fsm:
            with m.State("START"):
                m.d.sync += self.o_ready.eq(0)

                m.d.sync += self.r_colour.eq(self.i_colour << 4)

                # The following mess calculates the reciprocal of i_dx
                # as a Q12.4 fixed-point number.
                m.d.sync += self.r_recip.eq(0)
                with m.If((self.i_dx >= 0) & (self.i_dx < 1)): m.d.sync += self.r_recip.eq(0)
                with m.If((self.i_dx >= 1) & (self.i_dx < 2)): m.d.sync += self.r_recip.eq(4096)
                with m.If((self.i_dx >= 2) & (self.i_dx < 3)): m.d.sync += self.r_recip.eq(2048)
                with m.If((self.i_dx >= 3) & (self.i_dx < 4)): m.d.sync += self.r_recip.eq(1365)
                with m.If((self.i_dx >= 4) & (self.i_dx < 5)): m.d.sync += self.r_recip.eq(1024)
                with m.If((self.i_dx >= 5) & (self.i_dx < 6)): m.d.sync += self.r_recip.eq(819)
                with m.If((self.i_dx >= 6) & (self.i_dx < 7)): m.d.sync += self.r_recip.eq(682)
                with m.If((self.i_dx >= 7) & (self.i_dx < 8)): m.d.sync += self.r_recip.eq(585)
                with m.If((self.i_dx >= 8) & (self.i_dx < 9)): m.d.sync += self.r_recip.eq(512)
                with m.If((self.i_dx >= 9) & (self.i_dx < 10)): m.d.sync += self.r_recip.eq(455)
                with m.If((self.i_dx >= 10) & (self.i_dx < 11)): m.d.sync += self.r_recip.eq(409)
                with m.If((self.i_dx >= 11) & (self.i_dx < 12)): m.d.sync += self.r_recip.eq(372)
                with m.If((self.i_dx >= 12) & (self.i_dx < 13)): m.d.sync += self.r_recip.eq(341)
                with m.If((self.i_dx >= 13) & (self.i_dx < 14)): m.d.sync += self.r_recip.eq(315)
                with m.If((self.i_dx >= 14) & (self.i_dx < 15)): m.d.sync += self.r_recip.eq(292)
                with m.If((self.i_dx >= 15) & (self.i_dx < 16)): m.d.sync += self.r_recip.eq(273)
                with m.If((self.i_dx >= 16) & (self.i_dx < 17)): m.d.sync += self.r_recip.eq(256)
                with m.If((self.i_dx >= 17) & (self.i_dx < 18)): m.d.sync += self.r_recip.eq(240)
                with m.If((self.i_dx >= 18) & (self.i_dx < 19)): m.d.sync += self.r_recip.eq(227)
                with m.If((self.i_dx >= 19) & (self.i_dx < 20)): m.d.sync += self.r_recip.eq(215)
                with m.If((self.i_dx >= 20) & (self.i_dx < 21)): m.d.sync += self.r_recip.eq(204)
                with m.If((self.i_dx >= 21) & (self.i_dx < 22)): m.d.sync += self.r_recip.eq(195)
                with m.If((self.i_dx >= 22) & (self.i_dx < 23)): m.d.sync += self.r_recip.eq(186)
                with m.If((self.i_dx >= 23) & (self.i_dx < 24)): m.d.sync += self.r_recip.eq(178)
                with m.If((self.i_dx >= 24) & (self.i_dx < 25)): m.d.sync += self.r_recip.eq(170)
                with m.If((self.i_dx >= 25) & (self.i_dx < 26)): m.d.sync += self.r_recip.eq(163)
                with m.If((self.i_dx >= 26) & (self.i_dx < 27)): m.d.sync += self.r_recip.eq(157)
                with m.If((self.i_dx >= 27) & (self.i_dx < 28)): m.d.sync += self.r_recip.eq(151)
                with m.If((self.i_dx >= 28) & (self.i_dx < 29)): m.d.sync += self.r_recip.eq(146)
                with m.If((self.i_dx >= 29) & (self.i_dx < 30)): m.d.sync += self.r_recip.eq(141)
                with m.If((self.i_dx >= 30) & (self.i_dx < 31)): m.d.sync += self.r_recip.eq(136)
                with m.If((self.i_dx >= 31) & (self.i_dx < 32)): m.d.sync += self.r_recip.eq(132)
                with m.If((self.i_dx >= 32) & (self.i_dx < 33)): m.d.sync += self.r_recip.eq(128)
                with m.If((self.i_dx >= 33) & (self.i_dx < 34)): m.d.sync += self.r_recip.eq(124)
                with m.If((self.i_dx >= 34) & (self.i_dx < 35)): m.d.sync += self.r_recip.eq(120)
                with m.If((self.i_dx >= 35) & (self.i_dx < 36)): m.d.sync += self.r_recip.eq(117)
                with m.If((self.i_dx >= 36) & (self.i_dx < 37)): m.d.sync += self.r_recip.eq(113)
                with m.If((self.i_dx >= 37) & (self.i_dx < 38)): m.d.sync += self.r_recip.eq(110)
                with m.If((self.i_dx >= 38) & (self.i_dx < 39)): m.d.sync += self.r_recip.eq(107)
                with m.If((self.i_dx >= 39) & (self.i_dx < 40)): m.d.sync += self.r_recip.eq(105)
                with m.If((self.i_dx >= 40) & (self.i_dx < 41)): m.d.sync += self.r_recip.eq(102)
                with m.If((self.i_dx >= 41) & (self.i_dx < 42)): m.d.sync += self.r_recip.eq(99)
                with m.If((self.i_dx >= 42) & (self.i_dx < 43)): m.d.sync += self.r_recip.eq(97)
                with m.If((self.i_dx >= 43) & (self.i_dx < 44)): m.d.sync += self.r_recip.eq(95)
                with m.If((self.i_dx >= 44) & (self.i_dx < 45)): m.d.sync += self.r_recip.eq(93)
                with m.If((self.i_dx >= 45) & (self.i_dx < 46)): m.d.sync += self.r_recip.eq(91)
                with m.If((self.i_dx >= 46) & (self.i_dx < 47)): m.d.sync += self.r_recip.eq(89)
                with m.If((self.i_dx >= 47) & (self.i_dx < 48)): m.d.sync += self.r_recip.eq(87)
                with m.If((self.i_dx >= 48) & (self.i_dx < 49)): m.d.sync += self.r_recip.eq(85)
                with m.If((self.i_dx >= 49) & (self.i_dx < 50)): m.d.sync += self.r_recip.eq(83)
                with m.If((self.i_dx >= 50) & (self.i_dx < 51)): m.d.sync += self.r_recip.eq(81)
                with m.If((self.i_dx >= 51) & (self.i_dx < 52)): m.d.sync += self.r_recip.eq(80)
                with m.If((self.i_dx >= 52) & (self.i_dx < 53)): m.d.sync += self.r_recip.eq(78)
                with m.If((self.i_dx >= 53) & (self.i_dx < 54)): m.d.sync += self.r_recip.eq(77)
                with m.If((self.i_dx >= 54) & (self.i_dx < 55)): m.d.sync += self.r_recip.eq(75)
                with m.If((self.i_dx >= 55) & (self.i_dx < 56)): m.d.sync += self.r_recip.eq(74)
                with m.If((self.i_dx >= 56) & (self.i_dx < 57)): m.d.sync += self.r_recip.eq(73)
                with m.If((self.i_dx >= 57) & (self.i_dx < 58)): m.d.sync += self.r_recip.eq(71)
                with m.If((self.i_dx >= 58) & (self.i_dx < 59)): m.d.sync += self.r_recip.eq(70)
                with m.If((self.i_dx >= 59) & (self.i_dx < 60)): m.d.sync += self.r_recip.eq(69)
                with m.If((self.i_dx >= 60) & (self.i_dx < 61)): m.d.sync += self.r_recip.eq(68)
                with m.If((self.i_dx >= 61) & (self.i_dx < 62)): m.d.sync += self.r_recip.eq(67)
                with m.If((self.i_dx >= 62) & (self.i_dx < 63)): m.d.sync += self.r_recip.eq(66)
                with m.If((self.i_dx >= 63) & (self.i_dx < 64)): m.d.sync += self.r_recip.eq(65)
                with m.If((self.i_dx >= 64) & (self.i_dx < 65)): m.d.sync += self.r_recip.eq(64)
                with m.If((self.i_dx >= 65) & (self.i_dx < 66)): m.d.sync += self.r_recip.eq(63)
                with m.If((self.i_dx >= 66) & (self.i_dx < 67)): m.d.sync += self.r_recip.eq(62)
                with m.If((self.i_dx >= 67) & (self.i_dx < 68)): m.d.sync += self.r_recip.eq(61)
                with m.If((self.i_dx >= 68) & (self.i_dx < 69)): m.d.sync += self.r_recip.eq(60)
                with m.If((self.i_dx >= 69) & (self.i_dx < 70)): m.d.sync += self.r_recip.eq(59)
                with m.If((self.i_dx >= 70) & (self.i_dx < 71)): m.d.sync += self.r_recip.eq(58)
                with m.If((self.i_dx >= 71) & (self.i_dx < 72)): m.d.sync += self.r_recip.eq(57)
                with m.If((self.i_dx >= 72) & (self.i_dx < 74)): m.d.sync += self.r_recip.eq(56)
                with m.If((self.i_dx >= 74) & (self.i_dx < 75)): m.d.sync += self.r_recip.eq(55)
                with m.If((self.i_dx >= 75) & (self.i_dx < 76)): m.d.sync += self.r_recip.eq(54)
                with m.If((self.i_dx >= 76) & (self.i_dx < 78)): m.d.sync += self.r_recip.eq(53)
                with m.If((self.i_dx >= 78) & (self.i_dx < 79)): m.d.sync += self.r_recip.eq(52)
                with m.If((self.i_dx >= 79) & (self.i_dx < 81)): m.d.sync += self.r_recip.eq(51)
                with m.If((self.i_dx >= 81) & (self.i_dx < 82)): m.d.sync += self.r_recip.eq(50)
                with m.If((self.i_dx >= 82) & (self.i_dx < 84)): m.d.sync += self.r_recip.eq(49)
                with m.If((self.i_dx >= 84) & (self.i_dx < 86)): m.d.sync += self.r_recip.eq(48)
                with m.If((self.i_dx >= 86) & (self.i_dx < 88)): m.d.sync += self.r_recip.eq(47)
                with m.If((self.i_dx >= 88) & (self.i_dx < 90)): m.d.sync += self.r_recip.eq(46)
                with m.If((self.i_dx >= 90) & (self.i_dx < 92)): m.d.sync += self.r_recip.eq(45)
                with m.If((self.i_dx >= 92) & (self.i_dx < 94)): m.d.sync += self.r_recip.eq(44)
                with m.If((self.i_dx >= 94) & (self.i_dx < 96)): m.d.sync += self.r_recip.eq(43)
                with m.If((self.i_dx >= 96) & (self.i_dx < 98)): m.d.sync += self.r_recip.eq(42)
                with m.If((self.i_dx >= 98) & (self.i_dx < 100)): m.d.sync += self.r_recip.eq(41)
                with m.If((self.i_dx >= 100) & (self.i_dx < 103)): m.d.sync += self.r_recip.eq(40)
                with m.If((self.i_dx >= 103) & (self.i_dx < 106)): m.d.sync += self.r_recip.eq(39)
                with m.If((self.i_dx >= 106) & (self.i_dx < 108)): m.d.sync += self.r_recip.eq(38)
                with m.If((self.i_dx >= 108) & (self.i_dx < 111)): m.d.sync += self.r_recip.eq(37)
                with m.If((self.i_dx >= 111) & (self.i_dx < 114)): m.d.sync += self.r_recip.eq(36)
                with m.If((self.i_dx >= 114) & (self.i_dx < 118)): m.d.sync += self.r_recip.eq(35)
                with m.If((self.i_dx >= 118) & (self.i_dx < 121)): m.d.sync += self.r_recip.eq(34)
                with m.If((self.i_dx >= 121) & (self.i_dx < 125)): m.d.sync += self.r_recip.eq(33)
                with m.If((self.i_dx >= 125) & (self.i_dx < 129)): m.d.sync += self.r_recip.eq(32)
                with m.If((self.i_dx >= 129) & (self.i_dx < 133)): m.d.sync += self.r_recip.eq(31)
                with m.If((self.i_dx >= 133) & (self.i_dx < 137)): m.d.sync += self.r_recip.eq(30)
                with m.If((self.i_dx >= 137) & (self.i_dx < 142)): m.d.sync += self.r_recip.eq(29)
                with m.If((self.i_dx >= 142) & (self.i_dx < 147)): m.d.sync += self.r_recip.eq(28)
                with m.If((self.i_dx >= 147) & (self.i_dx < 152)): m.d.sync += self.r_recip.eq(27)
                with m.If((self.i_dx >= 152) & (self.i_dx < 158)): m.d.sync += self.r_recip.eq(26)
                with m.If((self.i_dx >= 158) & (self.i_dx < 164)): m.d.sync += self.r_recip.eq(25)
                with m.If((self.i_dx >= 164) & (self.i_dx < 171)): m.d.sync += self.r_recip.eq(24)
                with m.If((self.i_dx >= 171) & (self.i_dx < 179)): m.d.sync += self.r_recip.eq(23)
                with m.If((self.i_dx >= 179) & (self.i_dx < 187)): m.d.sync += self.r_recip.eq(22)
                with m.If((self.i_dx >= 187) & (self.i_dx < 196)): m.d.sync += self.r_recip.eq(21)
                with m.If((self.i_dx >= 196) & (self.i_dx < 205)): m.d.sync += self.r_recip.eq(20)
                with m.If((self.i_dx >= 205) & (self.i_dx < 216)): m.d.sync += self.r_recip.eq(19)
                with m.If((self.i_dx >= 216) & (self.i_dx < 228)): m.d.sync += self.r_recip.eq(18)
                with m.If((self.i_dx >= 228) & (self.i_dx < 241)): m.d.sync += self.r_recip.eq(17)
                with m.If((self.i_dx >= 241) & (self.i_dx < 257)): m.d.sync += self.r_recip.eq(16)
                with m.If((self.i_dx >= 257) & (self.i_dx < 274)): m.d.sync += self.r_recip.eq(15)
                with m.If((self.i_dx >= 274) & (self.i_dx < 293)): m.d.sync += self.r_recip.eq(14)
                with m.If((self.i_dx >= 293) & (self.i_dx < 316)): m.d.sync += self.r_recip.eq(13)
                with m.If((self.i_dx >= 316) & (self.i_dx < 342)): m.d.sync += self.r_recip.eq(12)
                with m.If((self.i_dx >= 342) & (self.i_dx < 373)): m.d.sync += self.r_recip.eq(11)
                with m.If((self.i_dx >= 373) & (self.i_dx < 410)): m.d.sync += self.r_recip.eq(10)
                with m.If((self.i_dx >= 410) & (self.i_dx < 456)): m.d.sync += self.r_recip.eq(9)
                with m.If((self.i_dx >= 456) & (self.i_dx < 513)): m.d.sync += self.r_recip.eq(8)
                with m.If((self.i_dx >= 513) & (self.i_dx < 586)): m.d.sync += self.r_recip.eq(7)
                with m.If((self.i_dx >= 586) & (self.i_dx < 683)): m.d.sync += self.r_recip.eq(6)
                with m.If((self.i_dx >= 683) & (self.i_dx < 820)): m.d.sync += self.r_recip.eq(5)
                with m.If((self.i_dx >= 820) & (self.i_dx < 1025)): m.d.sync += self.r_recip.eq(4)
                with m.If((self.i_dx >= 1025) & (self.i_dx < 1366)): m.d.sync += self.r_recip.eq(3)
                with m.If((self.i_dx >= 1366) & (self.i_dx < 2049)): m.d.sync += self.r_recip.eq(2)
                with m.If((self.i_dx >= 2049) & (self.i_dx < 4097)): m.d.sync += self.r_recip.eq(1)

                with m.If(self.i_start):
                    m.next = "RECIP"
                
            with m.State("RECIP"):
                m.d.sync += self.o_ready.eq(1)
                m.d.sync += self.o_result.eq(self.r_colour * self.r_recip)

            with m.State("DONE"):
                with m.If(self.i_reset):
                    m.next = "START"

        return m


# Source: https://github.com/ssloy/tinyrenderer/wiki/Lesson-1:-Bresenham%E2%80%99s-Line-Drawing-Algorithm#timings-fifth-and-final-attempt
class Bresenham(Elaboratable):
    def __init__(self):
        int_width    = 12
        frac_width   = 4
        width        = int_width + frac_width
        self.width   = width
        self.one     = 1 << frac_width

        # Input line coordinates
        self.i_x0    = Signal(width)
        self.i_y0    = Signal(width)
        self.i_x1    = Signal(width)
        self.i_y1    = Signal(width)

        # Input colours
        self.i_r0    = Signal(8)
        self.i_g0    = Signal(8)
        self.i_b0    = Signal(8)
        self.i_r1    = Signal(8)
        self.i_g1    = Signal(8)
        self.i_b1    = Signal(8)
        
        self.i_start = Signal() # Start processing line
        self.i_next  = Signal() # Advance to next pixel

        # Output pixel coordinates
        self.o_x     = Signal(int_width)
        self.o_y     = Signal(int_width)
        
        # Output pixel colour
        self.o_r     = Signal(8)
        self.o_g     = Signal(8)
        self.o_b     = Signal(8)

        self.o_valid = Signal() # Output pixel coordinates are valid
        self.o_last  = Signal() # Last pixel of the line

        self.r_steep = Signal() # True if line is transposed due to being steep (dy > dx)

        # Internal line coordinates; may be transposed due to line quadrant.
        self.r_x0    = Signal.like(self.i_x0)
        self.r_y0    = Signal.like(self.i_y0)
        self.r_x1    = Signal.like(self.i_x1)
        self.r_y1    = Signal.like(self.i_y1)

        # Internal pixel colours
        self.r_red   = Signal(self.width)
        self.r_green = Signal(self.width)
        self.r_blue  = Signal(self.width)

        # Internal pixel colour dividers
        self.r_rdiv  = ColourDivider()
        self.r_gdiv  = ColourDivider()
        self.r_bdiv  = ColourDivider()

        # Absolute change in X and Y.
        self.r_dx    = Signal.like(self.i_x0)
        self.r_dy    = Signal.like(self.i_y0)

        self.r_error = Signal.like(self.i_y0)
        self.r_y_inc = Signal((width, True))

    def elaborate(self, platform):
        m = Module()

        m.submodules.rdiv = self.r_rdiv
        m.submodules.gdiv = self.r_gdiv
        m.submodules.bdiv = self.r_bdiv

        with m.FSM() as fsm:
            with m.State("START"):
                # Reset output signals
                m.d.sync += [
                    self.o_valid.eq(0),
                    self.o_last.eq(0)
                ]

                # Transpose the coordinates so we're always in the positive X and Y quadrant.
                dx = Signal((self.width + 1, True))
                dy = Signal((self.width + 1, True))
                m.d.comb += [
                    dx.eq(self.i_x0 - self.i_x1),
                    dy.eq(self.i_y0 - self.i_y1)
                ]

                m.d.sync += [
                    self.r_x0.eq(self.i_x0),
                    self.r_y0.eq(self.i_y0),
                    self.r_x1.eq(self.i_x1),
                    self.r_y1.eq(self.i_y1),

                    self.r_dx.eq(Mux(dx < 0, -dx, dx)),
                    self.r_dy.eq(Mux(dy < 0, -dy, dy))
                ]

                m.d.sync += [
                    self.r_red.eq(self.i_r0 << 4),
                    self.r_green.eq(self.i_g0 << 4),
                    self.r_blue.eq(self.i_b0 << 4),

                    self.r_rdiv.i_colour.eq((self.i_r1 - self.i_r0) << 4),
                    self.r_gdiv.i_colour.eq((self.i_g1 - self.i_g0) << 4),
                    self.r_bdiv.i_colour.eq((self.i_b1 - self.i_b0) << 4),
                ]

                with m.If(self.i_start):
                    m.next = "TRANSPOSE"

            with m.State("TRANSPOSE"):
                # Transpose if the angle is steep.
                steep = Signal()
                m.d.comb += steep.eq(self.r_dx < self.r_dy),
                m.d.sync += [
                    self.r_steep.eq(steep),

                    self.r_x0.eq(Mux(steep, self.r_y0, self.r_x0)),
                    self.r_y0.eq(Mux(steep, self.r_x0, self.r_y0)),
                    self.r_x1.eq(Mux(steep, self.r_y1, self.r_x1)),
                    self.r_y1.eq(Mux(steep, self.r_x1, self.r_y1)),

                    self.r_dx.eq(Mux(steep, self.r_dy, self.r_dx)),
                    self.r_dy.eq(Mux(steep, self.r_dx, self.r_dy))
                ]

                m.d.sync += [
                    self.r_rdiv.i_start.eq(1),
                    self.r_gdiv.i_start.eq(1),
                    self.r_bdiv.i_start.eq(1),

                    self.r_rdiv.i_dx.eq(self.r_dx),
                    self.r_gdiv.i_dx.eq(self.r_dx),
                    self.r_bdiv.i_dx.eq(self.r_dx)
                ]

                m.next = "FLIP"

            with m.State("FLIP"):
                # (x0, y0) should be the bottom left coordinate.
                flip = Signal()
                m.d.comb += flip.eq(self.r_x1 < self.r_x0)

                m.d.sync += [
                    self.r_error.eq(0),
                    self.r_y_inc.eq(Mux(flip ^ (self.r_y0 < self.r_y1), +self.one, -self.one))
                ]

                m.d.sync += [
                    self.r_x0.eq(Mux(flip, self.r_x1, self.r_x0)),
                    self.r_y0.eq(Mux(flip, self.r_y1, self.r_y0)),
                    self.r_x1.eq(Mux(flip, self.r_x0, self.r_x1)),
                    self.r_y1.eq(Mux(flip, self.r_y0, self.r_y1))
                ]

                m.next = "NEXT-PIXEL"

            with m.State("NEXT-PIXEL"):
                # Output current coordinates
                m.d.sync += [
                    self.o_x.eq(Mux(self.r_steep, self.r_y0, self.r_x0) >> 4),
                    self.o_y.eq(Mux(self.r_steep, self.r_x0, self.r_y0) >> 4),

                    self.o_r.eq(self.r_red >> 4),
                    self.o_g.eq(self.r_green >> 4),
                    self.o_b.eq(self.r_blue >> 4),

                    self.o_valid.eq(1),
                    self.o_last.eq(self.r_x0 > self.r_x1)
                ]

                # Calculate next coordinates
                m.d.sync += [
                    self.r_error.eq(self.r_error + (self.r_dy << 1)),
                    self.r_x0.eq(self.r_x0 + self.one),

                    self.r_red.eq(self.r_red + self.r_rdiv.o_result),
                    self.r_green.eq(self.r_green + self.r_gdiv.o_result),
                    self.r_blue.eq(self.r_blue + self.r_bdiv.o_result)
                ]

                with m.If(self.o_last):
                    m.next = "FINISH"
                with m.Else():
                    m.next = "WAIT"
                
            # Wait for pixel acknowledgement before continuing.
            # While waiting, pre-calculate the next coordinates.
            with m.State("WAIT"):
                # If error goes above threshold, update Y
                with m.If(self.r_error > self.r_dx):
                    m.d.sync += [
                        self.r_y0.eq(self.r_y0 + self.r_y_inc),
                        self.r_error.eq(self.r_error - (self.r_dx << 1))
                    ]

                with m.If(self.i_next):
                    m.next = "NEXT-PIXEL"

            # Wait for pixel acknowledgement before resetting.
            with m.State("FINISH"):
                m.d.sync += [
                    self.r_rdiv.i_reset.eq(1),
                    self.r_gdiv.i_reset.eq(1),
                    self.r_bdiv.i_reset.eq(1)
                ]

                with m.If(self.i_next):
                    m.next = "START"

        return m


if __name__ == "__main__":
    dda = Bresenham()
    ports = [
        dda.i_x0, dda.i_y0, dda.i_r0, dda.i_g0, dda.i_b0,
        dda.i_x1, dda.i_y1, dda.i_r1, dda.i_g1, dda.i_b1,
        dda.i_start, dda.i_next,
        dda.o_x, dda.o_y,
        dda.o_valid, dda.o_last
    ]

    gtkw = open("sim.gtkw", "w")
    vcd = open("sim.vcd", "w")

    with open("line.v", "w") as f:
        f.write(verilog.convert(dda, ports=ports))

    with open("line.il", "w") as f:
        f.write(rtlil.convert(dda, ports=ports))
    
    def line_test(start, end, points):
        print("// ", start, "-> ", end)
        yield dda.i_x0.eq(start[0] << 4)
        yield dda.i_y0.eq(start[1] << 4)
        yield dda.i_x1.eq(end[0] << 4)
        yield dda.i_y1.eq(end[1] << 4)
        yield dda.i_start.eq(1)
        yield dda.i_next.eq(0)
        
        # Wait for setup
        yield; yield
        yield dda.i_start.eq(0)
        yield; yield; yield

        assert (yield dda.o_valid)

        for p in points:
            o_x = yield dda.o_x
            o_y = yield dda.o_y
            o_last_pixel = yield dda.o_last

            print("// ", (o_x, o_y), p)
            assert (o_x, o_y) == p

            yield dda.i_next.eq(1)
            yield; yield
            yield dda.i_next.eq(0)
            yield

    # 45 degree diagonals

    def line45():
        yield from line_test(
            start=(0, 0),
            end=(10, 10),
            points=[
                (0, 0),
                (1, 1),
                (2, 2),
                (3, 3),
                (4, 4),
                (5, 5),
                (6, 6),
                (7, 7),
                (8, 8),
                (9, 9),
                (10, 10)
            ]
        )

    def line135():
        yield from line_test(
            start=(0, 10),
            end=(10, 0),
            points=[
                (0, 10),
                (1, 9),
                (2, 8),
                (3, 7),
                (4, 6),
                (5, 5),
                (6, 4),
                (7, 3),
                (8, 2),
                (9, 1),
                (10, 0)
            ]
        )

    def line225():
        yield from line_test(
            start=(10, 10),
            end=(0, 0),
            points=[
                (0, 0),
                (1, 1),
                (2, 2),
                (3, 3),
                (4, 4),
                (5, 5),
                (6, 6),
                (7, 7),
                (8, 8),
                (9, 9),
                (10, 10)
            ]
        )

    def line315():
        yield from line_test(
            start=(10, 0),
            end=(0, 10),
            points=[
                (0, 10),
                (1, 9),
                (2, 8),
                (3, 7),
                (4, 6),
                (5, 5),
                (6, 4),
                (7, 3),
                (8, 2),
                (9, 1),
                (10, 0)
            ]
        )

    with pysim.Simulator(dda, gtkw_file=gtkw, vcd_file=vcd) as sim:
        sim.add_sync_process(line45)
        sim.add_clock(1e-6)
        sim.run()

    with pysim.Simulator(dda) as sim:
        sim.add_sync_process(line135)
        sim.add_clock(1e-6)
        sim.run()

    with pysim.Simulator(dda) as sim:
        sim.add_sync_process(line225)
        sim.add_clock(1e-6)
        sim.run()

    with pysim.Simulator(dda) as sim:
        sim.add_sync_process(line315)
        sim.add_clock(1e-6)
        sim.run()

    # Straight lines

    def line0():
        yield from line_test(
            start=(0, 0),
            end=(0, 10),
            points=[
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (0, 5),
                (0, 6),
                (0, 7),
                (0, 8),
                (0, 9),
                (0, 10)
            ]
        )

    def line90():
        yield from line_test(
            start=(0, 0),
            end=(10, 0),
            points=[
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (4, 0),
                (5, 0),
                (6, 0),
                (7, 0),
                (8, 0),
                (9, 0),
                (10, 0)
            ]
        )

    def line180():
        yield from line_test(
            start=(0, 10),
            end=(0, 0),
            points=[
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (0, 5),
                (0, 6),
                (0, 7),
                (0, 8),
                (0, 9),
                (0, 10)
            ]
        )

    def line270():
        yield from line_test(
            start=(10, 0),
            end=(0, 0),
            points=[
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (4, 0),
                (5, 0),
                (6, 0),
                (7, 0),
                (8, 0),
                (9, 0),
                (10, 0)
            ]
        )

    with pysim.Simulator(dda) as sim:
        sim.add_sync_process(line0)
        sim.add_clock(1e-6)
        sim.run()

    with pysim.Simulator(dda) as sim:
        sim.add_sync_process(line90)
        sim.add_clock(1e-6)
        sim.run()

    with pysim.Simulator(dda) as sim:
        sim.add_sync_process(line180)
        sim.add_clock(1e-6)
        sim.run()

    with pysim.Simulator(dda) as sim:
        sim.add_sync_process(line270)
        sim.add_clock(1e-6)
        sim.run()

    print("/*** UNIT TESTS PASSED ***/")
