from nmigen import Elaboratable, Module, Record, Signal
from nmigen.back import verilog

from common import Register
from pixel_pipeline import PixelPipeline


PIPE = [
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

    ("o_rgbrndr", 1),
    ("o_arndr", 1),
    ("o_zrndr", 1),

    ("o_x_coord", 16),
    ("o_y_coord", 16),
    ("o_z_coord", 32),

    ("o_red", 8),
    ("o_green", 8),
    ("o_blue", 8),
    ("o_alpha", 8)
]

class PipelineGroup(Elaboratable):
    def __init__(self, width):
        self.width        = width

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
        self.i_dimx_dm    = [[Signal((3, True)) for i in range(4)] for i in range(4)]

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

        self.pipes        = [Record(PIPE) for i in range(width)]

        self.i_address    = Signal(9)  # 8-bit address, plus "privilege" bit
        self.i_data       = Signal(64)

    def _add_pipeline_settings(self, m, pipe, rec):
        m.d.sync += [
            pipe.i_blend_a.eq(self.i_blend_a),
            pipe.i_blend_b.eq(self.i_blend_b),
            pipe.i_blend_c.eq(self.i_blend_c),
            pipe.i_blend_d.eq(self.i_blend_d),
            pipe.i_blend_fix.eq(self.i_blend_fix),

            pipe.i_pabe_pabe.eq(self.i_pabe_pabe),

            pipe.i_prim_abe.eq(self.i_prim_abe),

            pipe.i_test_ate.eq(self.i_test_ate),
            pipe.i_test_atst.eq(self.i_test_atst),
            pipe.i_test_aref.eq(self.i_test_aref),
            pipe.i_test_afail.eq(self.i_test_afail),
            pipe.i_test_date.eq(self.i_test_date),
            pipe.i_test_datm.eq(self.i_test_datm),
            pipe.i_test_zte.eq(self.i_test_zte),
            pipe.i_test_ztst.eq(self.i_test_ztst),

            pipe.i_dimx_dm00.eq(self.i_dimx_dm[0][0]),
            pipe.i_dimx_dm01.eq(self.i_dimx_dm[0][1]),
            pipe.i_dimx_dm02.eq(self.i_dimx_dm[0][2]),
            pipe.i_dimx_dm03.eq(self.i_dimx_dm[0][3]),
            pipe.i_dimx_dm10.eq(self.i_dimx_dm[1][0]),
            pipe.i_dimx_dm11.eq(self.i_dimx_dm[1][1]),
            pipe.i_dimx_dm12.eq(self.i_dimx_dm[1][2]),
            pipe.i_dimx_dm13.eq(self.i_dimx_dm[1][3]),
            pipe.i_dimx_dm20.eq(self.i_dimx_dm[2][0]),
            pipe.i_dimx_dm21.eq(self.i_dimx_dm[2][1]),
            pipe.i_dimx_dm22.eq(self.i_dimx_dm[2][2]),
            pipe.i_dimx_dm23.eq(self.i_dimx_dm[2][3]),
            pipe.i_dimx_dm30.eq(self.i_dimx_dm[3][0]),
            pipe.i_dimx_dm31.eq(self.i_dimx_dm[3][1]),
            pipe.i_dimx_dm32.eq(self.i_dimx_dm[3][2]),
            pipe.i_dimx_dm33.eq(self.i_dimx_dm[3][3]),

            pipe.i_dthe_dthe.eq(self.i_dthe_dthe),

            pipe.i_colclamp.eq(self.i_colclamp),
            pipe.i_fba_fba.eq(self.i_fba_fba),

            pipe.i_frame_psm.eq(self.i_frame_psm),
            pipe.i_zbuf_psm.eq(self.i_zbuf_psm),

            pipe.i_rgbrndr.eq(rec.i_rgbrndr),
            pipe.i_arndr.eq(rec.i_arndr),
            pipe.i_zrndr.eq(rec.i_zrndr),

            pipe.i_x_coord.eq(rec.i_x_coord),
            pipe.i_y_coord.eq(rec.i_y_coord),
            pipe.i_z_coord.eq(rec.i_z_coord),

            pipe.i_red.eq(rec.i_red),
            pipe.i_green.eq(rec.i_green),
            pipe.i_blue.eq(rec.i_blue),
            pipe.i_alpha.eq(rec.i_alpha),

            rec.o_rgbrndr.eq(pipe.o_rgbrndr),
            rec.o_arndr.eq(pipe.o_arndr),
            rec.o_zrndr.eq(pipe.o_zrndr),

            rec.o_x_coord.eq(pipe.o_x_coord),
            rec.o_y_coord.eq(pipe.o_y_coord),
            rec.o_z_coord.eq(pipe.o_z_coord),

            rec.o_red.eq(pipe.o_red),
            rec.o_green.eq(pipe.o_green),
            rec.o_blue.eq(pipe.o_blue),
            rec.o_alpha.eq(pipe.o_alpha)
        ]

    def elaborate(self, platform):
        m = Module()

        for i in range(self.width):
            m.submodules["pipe{:02}".format(i)] = pipe = PixelPipeline()
            self._add_pipeline_settings(m, pipe, self.pipes[i])

        with m.FSM():
            with m.State("READ"):
                with m.Switch(self.i_address):
                    with m.Case(Register.ALPHA_1):
                        # TODO: Multiple rendering contexts
                    with m.Case(Register.DIMX):
                        for x in range(4):
                            for y in range(4):
                                index = 16*x + 4*y
                                m.d.sync += self.i_dimx_dm[x][y].eq(self.i_data[index:index+3])

        return m


if __name__ == '__main__':
    width = 16
    pipe = PipelineGroup(width)

    ports = [
        pipe.i_blend_a, pipe.i_blend_b, pipe.i_blend_c, pipe.i_blend_d, pipe.i_blend_fix,
        pipe.i_prim_abe,
        pipe.i_test_ate, pipe.i_test_atst, pipe.i_test_aref, pipe.i_test_afail,
        pipe.i_test_date, pipe.i_test_datm,
        pipe.i_test_zte, pipe.i_test_ztst,
        pipe.i_colclamp,
        pipe.i_fba_fba,
        pipe.i_frame_psm, pipe.i_zbuf_psm,
        pipe.i_address,
        pipe.i_data,
    ]

    for i in range(width):
        ports += [
            pipe.pipes[i].i_rgbrndr, pipe.pipes[i].i_arndr, pipe.pipes[i].i_zrndr,
            pipe.pipes[i].i_x_coord, pipe.pipes[i].i_y_coord, pipe.pipes[i].i_z_coord,
            pipe.pipes[i].i_red, pipe.pipes[i].i_green, pipe.pipes[i].i_blue, pipe.pipes[i].i_alpha,
            pipe.pipes[i].o_rgbrndr, pipe.pipes[i].o_arndr, pipe.pipes[i].o_zrndr,
            pipe.pipes[i].o_x_coord, pipe.pipes[i].o_y_coord, pipe.pipes[i].o_z_coord,
            pipe.pipes[i].o_red, pipe.pipes[i].o_green, pipe.pipes[i].o_blue, pipe.pipes[i].o_alpha,
        ]

    # print(ports)

    print(verilog.convert(pipe, ports=ports))
