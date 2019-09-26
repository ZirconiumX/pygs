from enum import IntEnum
from nmigen import Elaboratable, Signal, Module
from nmigen.back import rtlil


class BlendRGB(IntEnum):
    SRC  = 0 # Use source channel value
    FB   = 1 # Use framebuffer channel value
    ZERO = 2 # Always-zero value


class BlendAlpha(IntEnum):
    SRC  = 0 # Use source channel value
    FB   = 1 # Use framebuffer channel value
    FIX  = 2 # Use FIX as alpha value


class AlphaBlend(Elaboratable):
    def __init__(self):
        self.i_enable  = Signal()   # Whether to alpha blend; Off or On.
        self.i_alphaen = Signal()   # Whether the high bit of the source alpha determines whether to alpha blend.

        self.i_fix     = Signal(8)  # Q8.0; Fixed alpha value

        # Blending is performed according to the following equation:
        # (((A - B) * C) >> 7) + D

        self.i_blend_a = Signal(2)  # Blending Parameter A; see BlendRGB
        self.i_blend_b = Signal(2)  # Blending Parameter B; see BlendRGB
        self.i_blend_c = Signal(2)  # Blending Parameter C; see BlendAlpha
        self.i_blend_d = Signal(2)  # Blending Parameter D; see BlendRGB

        self.i_fbred   = Signal(8)  # Q8.0; Framebuffer Red Channel
        self.i_fbgreen = Signal(8)  # Q8.0; Framebuffer Green Channel
        self.i_fbblue  = Signal(8)  # Q8.0; Framebuffer Blue Channel
        self.i_fbalpha = Signal(8)  # Q8.0; Framebuffer Alpha (Transparency) Channel

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

        self.i_fbpxfmt = Signal(6)  # Framebuffer Pixel Format

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

        a_red = Signal(8)
        a_green = Signal(8)
        a_blue = Signal(8)
        with m.Switch(self.i_blend_a):
            with m.Case(BlendRGB.SRC):
                m.d.comb += a_red.eq(self.i_red)
                m.d.comb += a_green.eq(self.i_green)
                m.d.comb += a_blue.eq(self.i_blue)
            with m.Case(BlendRGB.FB):
                m.d.comb += a_red.eq(self.i_fbred)
                m.d.comb += a_green.eq(self.i_fbgreen)
                m.d.comb += a_blue.eq(self.i_fbblue)
            with m.Case(BlendRGB.ZERO):
                m.d.comb += a_red.eq(0)
                m.d.comb += a_green.eq(0)
                m.d.comb += a_blue.eq(0)

        b_red = Signal(8)
        b_green = Signal(8)
        b_blue = Signal(8)
        with m.Switch(self.i_blend_b):
            with m.Case(BlendRGB.SRC):
                m.d.comb += b_red.eq(self.i_red)
                m.d.comb += b_green.eq(self.i_green)
                m.d.comb += b_blue.eq(self.i_blue)
            with m.Case(BlendRGB.FB):
                m.d.comb += b_red.eq(self.i_fbred)
                m.d.comb += b_green.eq(self.i_fbgreen)
                m.d.comb += b_blue.eq(self.i_fbblue)
            with m.Case(BlendRGB.ZERO):
                m.d.comb += b_red.eq(0)
                m.d.comb += b_green.eq(0)
                m.d.comb += b_blue.eq(0)

        c = Signal(8)
        with m.Switch(self.i_blend_c):
            with m.Case(BlendAlpha.SRC):
                m.d.comb += c.eq(self.i_alpha)
            with m.Case(BlendAlpha.FB):
                m.d.comb += c.eq(self.i_fbalpha)
            with m.Case(BlendAlpha.FIX):
                m.d.comb += c.eq(self.i_fix)

        d_red = Signal(8)
        d_green = Signal(8)
        d_blue = Signal(8)
        with m.Switch(self.i_blend_d):
            with m.Case(BlendRGB.SRC):
                m.d.comb += d_red.eq(self.i_red)
                m.d.comb += d_green.eq(self.i_green)
                m.d.comb += d_blue.eq(self.i_blue)
            with m.Case(BlendRGB.FB):
                m.d.comb += d_red.eq(self.i_fbred)
                m.d.comb += d_green.eq(self.i_fbgreen)
                m.d.comb += d_blue.eq(self.i_fbblue)
            with m.Case(BlendRGB.ZERO):
                m.d.comb += d_red.eq(0)
                m.d.comb += d_green.eq(0)
                m.d.comb += d_blue.eq(0)

        with m.If(self.i_enable & (~self.i_alphaen | self.i_alpha[7])):
            m.d.sync += [
                self.o_red.eq((((a_red - b_red) * c) >> 7) + d_red),
                self.o_green.eq((((a_green - b_green) * c) >> 7) + d_green),
                self.o_blue.eq((((a_blue - b_blue) * c) >> 7) + d_blue)
            ]
        with m.Else():
            m.d.sync += [
                self.o_red.eq(self.i_red),
                self.o_green.eq(self.i_green),
                self.o_blue.eq(self.i_blue)
            ]

        return m

if __name__ == "__main__":
    ablend = AlphaBlend()

    ports = [
        ablend.i_enable, ablend.i_alphaen, ablend.i_fix,

        ablend.i_blend_a, ablend.i_blend_b, ablend.i_blend_c, ablend.i_blend_d,
        ablend.i_fbred, ablend.i_fbgreen, ablend.i_fbblue, ablend.i_fbalpha,

        ablend.i_rgbrndr, ablend.i_arndr, ablend.i_zrndr,
        ablend.i_x_coord, ablend.i_y_coord, ablend.i_z_coord,
        ablend.i_red, ablend.i_green, ablend.i_blue, ablend.i_alpha,
        ablend.i_fbpxfmt,

        ablend.o_rgbrndr, ablend.o_arndr, ablend.o_zrndr,
        ablend.o_x_coord, ablend.o_y_coord, ablend.o_z_coord,
        ablend.o_red, ablend.o_green, ablend.o_blue, ablend.o_alpha,
    ]

    print(rtlil.convert(ablend, ports=ports))
