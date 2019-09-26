from nmigen import Elaboratable, Module, Record, Signal
from nmigen.back import pysim


class Pcrtc(Elaboratable):
    def __init__(self):
        # Sources:
        # Documented registers: GS User's Manual, 6.0
        # Undocumented registers: http://psx-scene.com/forums/f291/gs-mode-selector-development-feedback-61808/#post457673

        # PMODE - PCRTC Mode
        self.pmode_en1      = Signal()   # Read Circuit 1 Enable; Off or On
        self.pmode_en2      = Signal()   # Read Circuit 2 Enable; Off or On
        self.pmode_crtmd    = Signal(3)  # CRT Output Switching; Always 001
        self.pmode_mmod     = Signal()   # Alpha Value for Alpha Blending; Read Circuit 1 or ALP register
        self.pmode_amod     = Signal()   # OUT1 Alpha Output Selection; Read Circuit 1 or Read Circuit 2
        self.pmode_slbg     = Signal()   # Alpha Blending Source; Blended with Read Circuit 2 or background colour
        self.pmode_alp      = Signal(8)  # Fixed Alpha Value; 0xFF = 1.0

        # SMODE1 - Low-level PCRTC Init
        self.smode1_rc      = Signal(3)  # PLL Reference Divider
        self.smode1_lc      = Signal(7)  # PLL Loop Divider
        self.smode1_t1248   = Signal(2)  # PLL Output Divider
        self.smode1_slck    = Signal()   # ???
        self.smode1_cmod    = Signal(2)  # Colour Mode; PAL, NTSC or VESA
        self.smode1_ex      = Signal()   # ???
        self.smode1_prst    = Signal()   # PLL Reset; Off or On
        self.smode1_sint    = Signal()   # PLL Enable; Off or On
        self.smode1_xpck    = Signal()   # ???
        self.smode1_pck2    = Signal(2)  # ???
        self.smode1_spml    = Signal(4)  # Sub-Pixel Magnification Level
        self.smode1_gcont   = Signal()   # Component Colour Space; RGB or YPbPr
        self.smode1_phs     = Signal()   # ???
        self.smode1_pvs     = Signal()   # ???
        self.smode1_pehs    = Signal()   # ???
        self.smode1_pevs    = Signal()   # ???
        self.smode1_clksel  = Signal(2)  # ???
        self.smode1_nvck    = Signal()   # ???
        self.smode1_slck2   = Signal()   # ???
        self.smode1_vcksel  = Signal(2)  # ???
        self.smode1_vhp     = Signal()   # Progressive or Interlaced
                                         # http://martin.hinner.info/vga/pal.html suggests VHP could function
                                         # by enabling or disabling odd/even frame pulses.

        # SMODE2 - Additional PCRTC Configuration
        self.smode2_int     = Signal()   # Interlacing; Off or On
        self.smode2_ffmd    = Signal()   # Field/Frame Mode; Field (read every other line) or Frame (read every line)
        self.smode2_dpms    = Signal(2)  # VESA DPMS; On, Standby, Suspend, Off

        # SRFSH - DRAM refresh timing
        self.srfsh_rfsh     = Signal(4)  # ???

        # SYNCH1 - Horizontal Sync settings
        self.synch1_hfp     = Signal(11) # Horizontal Front Porch
        self.synch1_hbp     = Signal(11) # Horizontal Back Porch
        self.synch1_hseq    = Signal(10) # ???
        self.synch1_hsvs    = Signal(11) # ???
        self.synch1_hs      = Signal(21) # Horizontal Sync

        # SYNCH2 - Additional Horizontal Sync settings
        self.synch2_hf      = Signal(11) # ???
        self.synch2_hb      = Signal(11) # ???

        # SYNCV - Vertical Sync Settings
        self.syncv_vfp      = Signal(10) # Vertical Front Porch
        self.syncv_vfpe     = Signal(10) # Vertical Front Porch End
        self.syncv_vbp      = Signal(12) # Vertical Back Porch
        self.syncv_vbpe     = Signal(10) # Vertical Back Porch End
        self.syncv_vdp      = Signal(11) # Vertical Differential Phase
        self.syncv_vs       = Signal(11) # Vertical Sync

        # DISPFB1 - Framebuffer Position for Read Circuit 1
        self.dispfb1_fbp    = Signal(9)  # Framebuffer Base Pointer / 2048
        self.dispfb1_fbw    = Signal(6)  # Framebuffer Width / 64
        self.dispfb1_psm    = Signal(5)  # Pixel Storage Format
        self.dispfb1_dbx    = Signal(11) # Upper Left X Coordinate of Framebuffer in VRAM
        self.dispfb1_dby    = Signal(11) # Upper Left Y Coordinate of Framebuffer in VRAM
        
        # DISPLAY1 - Display Position for Read Circuit 1
        self.display1_dx    = Signal(12) # Upper Left X Coordinate of Display Area in VRAM
        self.display1_dy    = Signal(11) # Upper Left Y Coordinate of Display Area in VRAM
        self.display1_magh  = Signal(4)  # Horizontal Magnification Minus One
        self.display1_magv  = Signal(2)  # Vertical Magnification Minus One
        self.display1_dw    = Signal(12) # Display Area Width Minus One in VCKs
        self.display1_dh    = Signal(11) # Display Area Height Minus One in Pixels

        # DISPFB2 - Framebuffer Position for Read Circuit 2
        self.dispfb2_fbp    = Signal(9)  # Framebuffer Base Pointer / 2048
        self.dispfb2_fbw    = Signal(6)  # Framebuffer Width / 64
        self.dispfb2_psm    = Signal(5)  # Pixel Storage Format
        self.dispfb2_dbx    = Signal(11) # Upper Left X Coordinate of Framebuffer in VRAM
        self.dispfb2_dby    = Signal(11) # Upper Left Y Coordinate of Framebuffer in VRAM

        # DISPLAY2 - Display Position for Read Circuit 2
        self.display2_dx    = Signal(12) # Upper Left X Coordinate of Display Area in VRAM
        self.display2_dy    = Signal(11) # Upper Left Y Coordinate of Display Area in VRAM
        self.display2_magh  = Signal(4)  # Horizontal Magnification Minus One
        self.display2_magv  = Signal(2)  # Vertical Magnification Minus One
        self.display2_dw    = Signal(12) # Display Area Width Minus One in VCKs
        self.display2_dh    = Signal(11) # Display Area Height Minus One in Pixels

        # EXTBUF - Feedback Buffer Settings
        self.extbuf_exbp    = Signal(14) # Base Pointer; Address / 64
        self.extbuf_exbw    = Signal(6)  # Buffer Width; Pixels / 64
        self.extbuf_fbin    = Signal(2)  # Framebuffer Input; OUT1 or OUT2
        self.extbuf_wffmd   = Signal()   # Interlace Mode; Field (every other raster) or Frame (every raster)
        self.extbuf_emoda   = Signal(2)  # Input Alpha Mode; Input Alpha, RGB to Luma, RGB to Luma divided by 2, or zero
        self.extbuf_emodc   = Signal(2)  # Input Colour Mode; Input RGB, RGB to Luma, RGB to YCbCr, or Input Alpha
        self.extbuf_wdx     = Signal(11) # Upper Left X Coordinate of External Input in VRAM
        self.extbuf_wdy     = Signal(11) # Upper Left Y Coordinate of External Input in VRAM

        # EXTDATA - Feedback PCRTC Settings
        self.extdata_sx     = Signal(12) # Upper Left X Coordinate of External Input in VCKs
        self.extdata_sy     = Signal(11) # Upper Left Y Coordinate of External Input in Pixels
        self.extdata_smph   = Signal(4)  # Horizontal Sampling Rate in VCKs
        self.extdata_smpv   = Signal(2)  # Vertical Sampling Rate in H-Syncs
        self.extdata_ww     = Signal(12) # Write Width Minus One
        self.extdata_wh     = Signal(11) # Write Height Minus One

        # EXTWRITE - Feedback Enable/Disable
        self.extwrite_write = Signal()   # Write Activation/Deactivation

        # BGCOLOR - Background colour
        self.bgcolor_r      = Signal(8)  # Red Channel
        self.bgcolor_g      = Signal(8)  # Green Channel
        self.bgcolor_b      = Signal(8)  # Blue Channel

        # Signal constants
        self.o_

        # Internal clocks
        self.i_pixclk       = Signal()   # Pixel clock
        self.r_hclk         = Signal(12) # Number of horizontal clocks
        self.r_vclk         = Signal(12) # Number of vertical clocks

        self.r_vfp          = Signal(12) # Start of Vertical Front Porch
        self.r_vsync        = Signal(12) # Start of Vertical Sync
        self.r_vbp          = Signal(12) # Start of Vertical Back Porch
        self.r_vact         = Signal(12) # Start of Active Signal
        self.r_vend         = Signal(12) # End of Frame

        self.r_hfp          = Signal(12)
        self.r_hsync        = Signal(12)
        self.r_hbp          = Signal(12)
        self.r_hact         = Signal(12)
        self.r_hend         = Signal(12)

        self.d_hblank       = Signal()   # In Horizontal Blanking Interval
        self.d_hfp          = Signal()   # In Horizontal Front Porch
        self.d_hsync        = Signal()   # In Horizontal Synchronisation
        self.d_hbp          = Signal()   # In Horizontal Back Porch

        self.d_vblank       = Signal()   # In Vertical Blanking Interval
        self.d_vfp          = Signal()   # In Vertical Front Porch
        self.d_vsync        = Signal()   # In Vertical Synchronisation
        self.d_vbp          = Signal()   # In Vertical Back Porch

    def elaborate(self, platform):
        m = Module()

        # PLL update
        # Reset the PLLs if asked to.
        with m.If(self.smode1_prst):
            m.d.sync += [
                self.r_hclk.eq(0),
                self.r_vclk.eq(0),

                self.r_hfp.eq(0),
                self.r_hsync.eq(self.synch1_hfp),
                self.r_hbp.eq(self.synch1_hfp + self.synch1_hs),
                self.r_hact.eq(self.synch1_hfp + self.synch1_hs + self.synch1_hbp),
                self.r_hend.eq(720),

                self.r_vfp.eq(0),
                self.r_vsync.eq(self.syncv_vfp + self.syncv_vfpe),
                self.r_vbp.eq(self.syncv_vfp + self.syncv_vfpe + self.syncv_vs),
                self.r_vact.eq(self.syncv_vfp + self.syncv_vfpe + self.syncv_vs + self.syncv_vbp + self.syncv_vbpe),
                self.r_vend.eq(self.syncv_vfp + self.syncv_vfpe + self.syncv_vs + self.syncv_vbp + self.syncv_vbpe + self.syncv_vdp)
            ]

        # Otherwise, update the counters when the PLLs are enabled.
        with m.Elif(self.i_pixclk & self.smode1_sint):
            m.d.sync += self.r_hclk.eq(self.r_hclk + 1)

            with m.If(self.r_hclk == (self.r_hend - 1)):
                m.d.sync += self.r_hclk.eq(0)
                m.d.sync += self.r_vclk.eq(self.r_vclk + 1)

            with m.If(self.r_vclk == (self.r_vend - 1)):
                m.d.sync += self.r_vclk.eq(0)

        m.d.sync += [
            self.d_hfp.eq(self.r_hclk < self.r_hsync),
            self.d_hsync.eq((self.r_hclk >= self.r_hsync) & (self.r_hclk < self.r_hbp)),
            self.d_hbp.eq((self.r_hclk >= self.r_hbp) & (self.r_hclk < self.r_hact)),
            self.d_hblank.eq(self.r_hclk < self.r_hact),

            self.d_vfp.eq(self.r_vclk < self.r_vsync),
            self.d_vsync.eq((self.r_vclk >= self.r_vsync) & (self.r_vclk < self.r_vbp)),
            self.d_vbp.eq((self.r_vclk >= self.r_vbp) & (self.r_vclk < self.r_vact)),
            self.d_vblank.eq(self.r_vclk < self.r_vact)
        ]

        return m


if __name__ == "__main__":
    pcrtc = Pcrtc()

    ports = [
        pcrtc.smode1_prst, pcrtc.smode1_sint,
       
        pcrtc.synch1_hs,
        pcrtc.synch1_hsvs,
        pcrtc.synch1_hseq,
        pcrtc.synch1_hbp,
        pcrtc.synch1_hfp,

        pcrtc.synch2_hb,
        pcrtc.synch2_hf,

        pcrtc.syncv_vfp, pcrtc.syncv_vfpe,
        pcrtc.syncv_vs,
        pcrtc.syncv_vbp, pcrtc.syncv_vbpe, 
        pcrtc.syncv_vdp,

        pcrtc.i_pixclk,

        pcrtc.d_vblank, pcrtc.d_vfp, pcrtc.d_vsync, pcrtc.d_vbp,
        pcrtc.d_hblank, pcrtc.d_hfp, pcrtc.d_hsync, pcrtc.d_hbp
    ]

    def pal_signal():
        # PAL
        yield pcrtc.synch1_hs.eq(254)
        # yield pcrtc.synch1_hsvs.eq(1474)
        # yield pcrtc.synch1_hseq.eq(127)
        yield pcrtc.synch1_hbp.eq(262)
        yield pcrtc.synch1_hfp.eq(48)

        # yield pcrtc.synch2_hb.eq(1680)
        # yield pcrtc.synch2_hf.eq(1212)

        yield pcrtc.syncv_vfp.eq(1)
        yield pcrtc.syncv_vfpe.eq(5)
        yield pcrtc.syncv_vbp.eq(33)
        yield pcrtc.syncv_vbpe.eq(5)
        yield pcrtc.syncv_vdp.eq(576)
        yield pcrtc.syncv_vs.eq(5)
        
        yield pcrtc.smode1_prst.eq(1)
        yield pcrtc.smode1_sint.eq(0)

        yield

        yield pcrtc.smode1_prst.eq(0)
        yield pcrtc.smode1_sint.eq(1)

        for i in range(625 * 720):
            yield pcrtc.i_pixclk.eq(1)
            yield
            yield pcrtc.i_pixclk.eq(0)
            yield

    with pysim.Simulator(pcrtc, gtkw_file=open("pal.gtkw", "w"), vcd_file=open("pal.vcd", "w")) as sim:
        sim.add_sync_process(pal_signal)
        sim.add_clock(1 / (625 * 720 * 50))
        sim.run()
