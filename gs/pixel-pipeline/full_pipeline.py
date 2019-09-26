from nmigen import Elaboratable, Module, Record, Signal

from pixel_pipeline import PixelPipeline


PIPE = Record([
    ("i_rgbrndr", 1),
    ("i_arndr", 1),
    ("i_zrndr", 1),
    
    ("i_x_coord", 16),
    ("i_y_coord", 16),
    ("i_z_coord", 32),

    ("i_red", 8),
    ("i_green", 8),
    ("i_blue", 8),
    ("i_alpha", 8),

    ("i_fbpxfmt", 6),
    ("i_zbfmt", 6),

    ("o_rgbrndr", 1),
    ("o_arndr", 1),
    ("o_zrndr", 1),

    ("o_x_coord", 16),
    ("o_y_coord", 16),
    ("o_z_coord", 32),

    ("o_red", 9),
    ("o_green", 9),
    ("o_blue", 9),
    ("o_alpha", 8)
])

class PipelineGroup(Elaboratable):
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

        self.pipe00       = PIPE()

    def _add_pipeline(self, m, pipe):
        m.d.sync += [
            pipe.i_blend_a.eq(self.i_blend_a),
            pipe.i_blend_b.eq(self.i_blend_b),
            pipe.i_blend_c.eq(self.i_blend_c),
            pipe.i_blend_d.eq(self.i_blend_d),
            pipe.i_blend_fix.eq(self.i_blend_fix),

    def elaborate(self, platform):

