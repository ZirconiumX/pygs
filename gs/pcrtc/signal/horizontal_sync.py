from nmigen import Elaboratable, Module, Signal
from nmigen.back import pysim


class HorizontalSignal(Elaboratable):
    def __init__(self):
        # SYNCH1 - Horizontal Sync settings
        self.synch1_hfp     = Signal(11) # Horizontal Front Porch
        self.synch1_hbp     = Signal(11) # Horizontal Back Porch
        self.synch1_hseq    = Signal(10) # ???
        self.synch1_hsvs    = Signal(11) # ???
        self.synch1_hs      = Signal(21) # Horizontal Sync

        # SYNCH2 - Additional Horizontal Sync settings
        self.synch2_hf      = Signal(11) # ???
        self.synch2_hb      = Signal(11) # ???

        # I/O signals
        self.i_pxclk        = Signal()   # Pixel Clock
        self.i_odd          = Signal()   # High if we're on an odd frame, for synchronisation

        self.o_hlclk        = Signal()   # Halfline Clock; high at middle and end of horizontal line

    def elaborate(self, platform):
        m = Module()

        return m
