from nmigen import Elaboratable, Module, Signal
from nmigen.back import rtlil, verilog

from alpha_blend import AlphaBlend
from alpha_test import AlphaTest
from clamp import Clamp
from dest_alpha_test import DestinationAlphaTest
from dither import Dither
from z_test import ZTest


class PixelPipeline(Elaboratable):
    def __init__(self):
        # ALPHA - Alpha Blending
        self.i_blend_a    = Signal(2) # Blending Parameter A; see BlendRGB
        self.i_blend_b    = Signal(2) # Blending Parameter B; see BlendRGB
        self.i_blend_c    = Signal(2) # Blending Parameter C; see BlendAlpha
        self.i_blend_d    = Signal(2) # Blending Parameter D; see BlendRGB
        self.i_blend_fix  = Signal(8) # Q8.0; Fixed alpha value

        # PABE - Per-Pixel Alpha Blending Enable
        self.i_pabe_pabe  = Signal()  # Whether to perform per-pixel alpha blending

        # PRIM/PRMODE - Primitive Settings
        self.i_prim_abe   = Signal()  # Whether to perform alpha blending

        # TEST - Pixel Test Settings
        self.i_test_ate   = Signal()  # Whether to perform alpha testing
        self.i_test_atst  = Signal(3) # Alpha test to perform
        self.i_test_aref  = Signal(8) # Reference alpha value
        self.i_test_afail = Signal(2) # Action to perform on test failure
        self.i_test_date  = Signal()  # Whether to perform destination alpha testing
        self.i_test_datm  = Signal()  # Destination alpha test comparison value
        self.i_test_zte   = Signal()  # Z test enable (buggy)
        self.i_test_ztst  = Signal(2) # Z test type

        # DIMX - Dither Matrix
        self.i_dimx_dm00  = Signal(8) # (0, 0) dither matrix
        self.i_dimx_dm01  = Signal(8) # (1, 0) dither matrix
        self.i_dimx_dm02  = Signal(8) # (2, 0) dither matrix
        self.i_dimx_dm03  = Signal(8) # (3, 0) dither matrix
        self.i_dimx_dm10  = Signal(8) # (0, 1) dither matrix
        self.i_dimx_dm11  = Signal(8) # (1, 1) dither matrix
        self.i_dimx_dm12  = Signal(8) # (2, 1) dither matrix
        self.i_dimx_dm13  = Signal(8) # (3, 1) dither matrix
        self.i_dimx_dm20  = Signal(8) # (0, 2) dither matrix
        self.i_dimx_dm21  = Signal(8) # (1, 2) dither matrix
        self.i_dimx_dm22  = Signal(8) # (2, 2) dither matrix
        self.i_dimx_dm23  = Signal(8) # (3, 2) dither matrix
        self.i_dimx_dm30  = Signal(8) # (0, 3) dither matrix
        self.i_dimx_dm31  = Signal(8) # (1, 3) dither matrix
        self.i_dimx_dm32  = Signal(8) # (2, 3) dither matrix
        self.i_dimx_dm33  = Signal(8) # (3, 3) dither matrix

        # DTHE - Dither Enable
        self.i_dthe_dthe  = Signal()  # Whether to perform dithering

        # COLCLAMP - Colour Clamping Enable
        self.i_colclamp   = Signal()  # Whether to saturate or overflow colour channels

        # FBA - Framebuffer Alpha Correction value
        self.i_fba_fba    = Signal()  # Value ORed with most significant bit of alpha channel.

        # FRAME - Framebuffer Settings
        self.i_frame_psm  = Signal(6) # Framebuffer pixel storage format

        # ZBUF - Z Buffer Settings
        self.i_zbuf_psm   = Signal(4) # Z buffer pixel storage format

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

        self.o_red     = Signal(9)  # Output Red Channel
        self.o_green   = Signal(9)  # Output Green Channel
        self.o_blue    = Signal(9)  # Output Blue Channel
        self.o_alpha   = Signal(8)  # Output Alpha Channel

    def elaborate(self, platform):
        m = Module()
    
        m.submodules.alpha_test = alpha_test = AlphaTest()
        m.submodules.dest_alpha = dest_alpha = DestinationAlphaTest()
        m.submodules.z_test = z_test = ZTest()
        m.submodules.alpha_blend = alpha_blend = AlphaBlend()
        m.submodules.dither = dither = Dither()
        m.submodules.clamp = clamp = Clamp()

        m.d.sync += [
            # TODO: Is this synchronous or combinational? (Matters for timing)
            # input -> alpha_test
            alpha_test.i_enable.eq(self.i_test_ate),
            alpha_test.i_test.eq(self.i_test_atst),
            alpha_test.i_aref.eq(self.i_test_aref),
            alpha_test.i_failmod.eq(self.i_test_afail),

            alpha_test.i_rgbrndr.eq(self.i_rgbrndr),
            alpha_test.i_arndr.eq(self.i_arndr),
            alpha_test.i_zrndr.eq(self.i_zrndr),

            alpha_test.i_x_coord.eq(self.i_x_coord),
            alpha_test.i_y_coord.eq(self.i_y_coord),
            alpha_test.i_z_coord.eq(self.i_z_coord),

            alpha_test.i_red.eq(self.i_red),
            alpha_test.i_green.eq(self.i_green),
            alpha_test.i_blue.eq(self.i_blue),
            alpha_test.i_alpha.eq(self.i_alpha),

            alpha_test.i_fbpxfmt.eq(self.i_frame_psm),

            # alpha_test -> dest_alpha
            dest_alpha.i_enable.eq(self.i_test_date),
            dest_alpha.i_mode.eq(self.i_test_datm),

            dest_alpha.i_rgbrndr.eq(alpha_test.o_rgbrndr),
            dest_alpha.i_arndr.eq(alpha_test.o_arndr),
            dest_alpha.i_zrndr.eq(alpha_test.o_zrndr),

            dest_alpha.i_x_coord.eq(alpha_test.o_x_coord),
            dest_alpha.i_y_coord.eq(alpha_test.o_y_coord),
            dest_alpha.i_z_coord.eq(alpha_test.o_z_coord),

            dest_alpha.i_red.eq(alpha_test.o_red),
            dest_alpha.i_green.eq(alpha_test.o_green),
            dest_alpha.i_blue.eq(alpha_test.o_blue),
            dest_alpha.i_alpha.eq(alpha_test.o_alpha),

            dest_alpha.i_fbpxfmt.eq(self.i_frame_psm),
            
            # dest_alpha -> z_test
            z_test.i_enable.eq(self.i_test_zte),
            z_test.i_test.eq(self.i_test_ztst),
            z_test.i_zref.eq(0x7FFFFFFF),

            z_test.i_rgbrndr.eq(dest_alpha.o_rgbrndr),
            z_test.i_arndr.eq(dest_alpha.o_arndr),
            z_test.i_zrndr.eq(dest_alpha.o_zrndr),

            z_test.i_x_coord.eq(dest_alpha.o_x_coord),
            z_test.i_y_coord.eq(dest_alpha.o_y_coord),
            z_test.i_z_coord.eq(dest_alpha.o_z_coord),

            z_test.i_red.eq(dest_alpha.o_red),
            z_test.i_green.eq(dest_alpha.o_green),
            z_test.i_blue.eq(dest_alpha.o_blue),
            z_test.i_alpha.eq(dest_alpha.o_alpha),
            
            # z_test -> alpha_blend
            alpha_blend.i_blend_a.eq(self.i_blend_a),
            alpha_blend.i_blend_b.eq(self.i_blend_b),
            alpha_blend.i_blend_c.eq(self.i_blend_c),
            alpha_blend.i_blend_d.eq(self.i_blend_d),
            alpha_blend.i_fix.eq(self.i_blend_fix),
            
            alpha_blend.i_alphaen.eq(self.i_pabe_pabe),

            alpha_blend.i_enable.eq(self.i_prim_abe),

            alpha_blend.i_rgbrndr.eq(z_test.o_rgbrndr),
            alpha_blend.i_arndr.eq(z_test.o_arndr),
            alpha_blend.i_zrndr.eq(z_test.o_zrndr),

            alpha_blend.i_x_coord.eq(z_test.o_x_coord),
            alpha_blend.i_y_coord.eq(z_test.o_y_coord),
            alpha_blend.i_z_coord.eq(z_test.o_z_coord),

            alpha_blend.i_red.eq(z_test.o_red),
            alpha_blend.i_green.eq(z_test.o_green),
            alpha_blend.i_blue.eq(z_test.o_blue),
            alpha_blend.i_alpha.eq(z_test.o_alpha),

            alpha_blend.i_fbpxfmt.eq(self.i_frame_psm),

            # alpha_blend -> dither
            dither.i_enable.eq(self.i_dthe_dthe),

            dither.i_dm00.eq(self.i_dimx_dm00),
            dither.i_dm01.eq(self.i_dimx_dm01),
            dither.i_dm02.eq(self.i_dimx_dm02),
            dither.i_dm03.eq(self.i_dimx_dm03),
            dither.i_dm10.eq(self.i_dimx_dm10),
            dither.i_dm11.eq(self.i_dimx_dm11),
            dither.i_dm12.eq(self.i_dimx_dm12),
            dither.i_dm13.eq(self.i_dimx_dm13),
            dither.i_dm20.eq(self.i_dimx_dm20),
            dither.i_dm21.eq(self.i_dimx_dm21),
            dither.i_dm22.eq(self.i_dimx_dm22),
            dither.i_dm23.eq(self.i_dimx_dm23),
            dither.i_dm30.eq(self.i_dimx_dm30),
            dither.i_dm31.eq(self.i_dimx_dm31),
            dither.i_dm32.eq(self.i_dimx_dm32),
            dither.i_dm33.eq(self.i_dimx_dm33),

            dither.i_rgbrndr.eq(alpha_blend.o_rgbrndr),
            dither.i_arndr.eq(alpha_blend.o_arndr),
            dither.i_zrndr.eq(alpha_blend.o_zrndr),

            dither.i_x_coord.eq(alpha_blend.o_x_coord),
            dither.i_y_coord.eq(alpha_blend.o_y_coord),
            dither.i_z_coord.eq(alpha_blend.o_z_coord),

            dither.i_red.eq(alpha_blend.o_red),
            dither.i_green.eq(alpha_blend.o_green),
            dither.i_blue.eq(alpha_blend.o_blue),
            dither.i_alpha.eq(alpha_blend.o_alpha),

            # dither -> clamp
            clamp.i_clamp.eq(self.i_colclamp),
            clamp.i_alphcor.eq(self.i_fba_fba),

            clamp.i_rgbrndr.eq(dither.o_rgbrndr),
            clamp.i_arndr.eq(dither.o_arndr),
            clamp.i_zrndr.eq(dither.o_zrndr),

            clamp.i_x_coord.eq(dither.o_x_coord),
            clamp.i_y_coord.eq(dither.o_y_coord),
            clamp.i_z_coord.eq(dither.o_z_coord),

            clamp.i_red.eq(dither.o_red),
            clamp.i_green.eq(dither.o_green),
            clamp.i_blue.eq(dither.o_blue),
            clamp.i_alpha.eq(dither.o_alpha),

            # clamp -> output
            self.o_rgbrndr.eq(clamp.o_rgbrndr),
            self.o_arndr.eq(clamp.o_arndr),
            self.o_zrndr.eq(clamp.o_zrndr),

            self.o_x_coord.eq(clamp.o_x_coord),
            self.o_y_coord.eq(clamp.o_y_coord),
            self.o_z_coord.eq(clamp.o_z_coord),

            self.o_red.eq(clamp.o_red),
            self.o_green.eq(clamp.o_green),
            self.o_blue.eq(clamp.o_blue),
            self.o_alpha.eq(clamp.o_alpha)
         ]

        return m

if __name__ == "__main__":
    pipe = PixelPipeline()

    ports = [
        pipe.i_blend_a, pipe.i_blend_b, pipe.i_blend_c, pipe.i_blend_d, pipe.i_blend_fix,
        pipe.i_dimx_dm00, pipe.i_dimx_dm01, pipe.i_dimx_dm02, pipe.i_dimx_dm03,
        pipe.i_dimx_dm10, pipe.i_dimx_dm11, pipe.i_dimx_dm12, pipe.i_dimx_dm13,
        pipe.i_dimx_dm20, pipe.i_dimx_dm21, pipe.i_dimx_dm22, pipe.i_dimx_dm23,
        pipe.i_dimx_dm30, pipe.i_dimx_dm31, pipe.i_dimx_dm32, pipe.i_dimx_dm33,
        pipe.i_prim_abe,
        pipe.i_test_ate, pipe.i_test_atst, pipe.i_test_aref, pipe.i_test_afail,
        pipe.i_test_date, pipe.i_test_datm,
        pipe.i_test_zte, pipe.i_test_ztst,
        pipe.i_colclamp,
        pipe.i_fba_fba,
        pipe.i_frame_psm, pipe.i_zbuf_psm,

        pipe.i_rgbrndr, pipe.i_arndr, pipe.i_zrndr,
        pipe.i_x_coord, pipe.i_y_coord, pipe.i_z_coord,
        pipe.i_red, pipe.i_green, pipe.i_blue, pipe.i_alpha,

        pipe.o_rgbrndr, pipe.o_arndr, pipe.o_zrndr,
        pipe.o_x_coord, pipe.o_y_coord, pipe.o_z_coord,
        pipe.o_red, pipe.o_green, pipe.o_blue, pipe.o_alpha
    ]

    print(verilog.convert(pipe, ports=ports))
