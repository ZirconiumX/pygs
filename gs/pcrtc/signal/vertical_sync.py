from nmigen import Elaboratable, Signal, Module, Mux
from nmigen.back import pysim

class VerticalSignal(Elaboratable):
    def __init__(self):
        # SYNCV - Vertical Sync Settings
        self.syncv_vfp      = Signal(10) # Vertical Front Porch
        self.syncv_vfpe     = Signal(10) # Vertical Front Porch End
        self.syncv_vbp      = Signal(12) # Vertical Back Porch
        self.syncv_vbpe     = Signal(10) # Vertical Back Porch End
        self.syncv_vdp      = Signal(11) # Vertical Display
        self.syncv_vs       = Signal(11) # Vertical Sync

        self.i_hlclk        = Signal()   # Halfline Clock; high at end and middle of horizontal line

        self.o_odd          = Signal()   # High if we're on an odd frame, for synchronisation

        # Timing values
        self.r_vfp          = Signal(12) # Start of Vertical Front Porch
        self.r_vsync        = Signal(12) # Start of Vertical Sync
        self.r_vbp          = Signal(12) # Start of Vertical Back Porch
        self.r_vact         = Signal(12) # Start of Active Signal
        self.r_vend         = Signal(12) # End of Frame

        self.r_hline        = Signal(12, reset=1) # Number of halflines
        self.r_hline_count  = Signal(12, reset=1) # Number of halflines in current state

        # Debug signals
        self.d_vblank       = Signal()   # In Vertical Blanking Interval
        self.d_vfp          = Signal()   # In Vertical Front Porch
        self.d_vsync        = Signal()   # In Vertical Synchronisation
        self.d_vbp          = Signal()   # In Vertical Back Porch

    def elaborate(self, platform):
        m = Module()

        with m.If(self.i_hlclk):
            m.d.sync += [
                self.r_hline.eq(self.r_hline + 1),
                self.r_hline_count.eq(self.r_hline_count + 1),
            ]

            with m.FSM() as fsm:
                with m.State("SYNC"):
                    with m.If(self.r_hline_count == self.syncv_vs):
                        m.d.sync += self.r_hline_count.eq(1)
                        m.next = "BACK-PORCH"

                with m.State("BACK-PORCH"):
                    with m.If(self.r_hline_count == (self.syncv_vbp + self.syncv_vbpe)):
                        m.d.sync += self.r_hline_count.eq(1)
                        m.next = "DISPLAY"

                with m.State("DISPLAY"):
                    with m.If(self.r_hline_count == self.syncv_vdp):
                        m.d.sync += self.r_hline.eq(1)
                        m.d.sync += self.r_hline_count.eq(1)
                        m.next = "FRONT-PORCH"

                with m.State("FRONT-PORCH"):
                    with m.If(self.r_hline_count == (self.syncv_vfp + self.syncv_vfpe)):
                        m.d.sync += self.r_hline_count.eq(1)
                        m.d.sync += self.o_odd.eq(~self.o_odd)
                        m.next = "SYNC"

        return m

if __name__ == "__main__":
    vert = VerticalSignal()

    ports = [
        vert.syncv_vfp, vert.syncv_vfpe, vert.syncv_vbp, vert.syncv_vbpe, vert.syncv_vdp, vert.syncv_vs,

        vert.i_hlclk
    ]

    def pal():
        yield vert.syncv_vfp.eq(4)
        yield vert.syncv_vfpe.eq(5)
        yield vert.syncv_vbp.eq(33)
        yield vert.syncv_vbpe.eq(5)
        yield vert.syncv_vdp.eq(576)
        yield vert.syncv_vs.eq(5)

        for i in range(625 * 2):
            yield vert.i_hlclk.eq(1)
            yield
            yield vert.i_hlclk.eq(0)
            yield

    def ntsc():
        yield vert.syncv_vfp.eq(2)
        yield vert.syncv_vfpe.eq(6)
        yield vert.syncv_vbp.eq(26)
        yield vert.syncv_vbpe.eq(6)
        yield vert.syncv_vdp.eq(480)
        yield vert.syncv_vs.eq(6)

        for i in range(525 * 2):
            yield vert.i_hlclk.eq(1)
            yield
            yield vert.i_hlclk.eq(0)
            yield

    with pysim.Simulator(
            vert,
            gtkw_file=open("vertical-pal.gtkw", "w"),
            vcd_file=open("vertical-pal.vcd", "w")
            ) as sim:
        sim.add_sync_process(pal)
        sim.add_clock(1 / (625 * 50 * 4))
        sim.run()

    with pysim.Simulator(
            vert,
            gtkw_file=open("vertical-ntsc.gtkw", "w"),
            vcd_file=open("vertical-ntsc.vcd", "w")
            ) as sim:
        sim.add_sync_process(ntsc)
        sim.add_clock(1 / (525 * 60 * 4))
        sim.run()
