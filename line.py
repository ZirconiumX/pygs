from nmigen import Cat, Const, Elaboratable, Module, Mux, Signal
from nmigen.back import pysim, verilog


# Source: https://github.com/ssloy/tinyrenderer/wiki/Lesson-1:-Bresenham%E2%80%99s-Line-Drawing-Algorithm#timings-fifth-and-final-attempt
class Bresenham(Elaboratable):
    def __init__(self, real_width, frac_width):
        assert (real_width + frac_width) >= 1

        width        = real_width + frac_width
        self.width   = width
        self.one     = 1 << frac_width

        # Input line coordinates
        self.i_x0    = Signal(width)
        self.i_y0    = Signal(width)
        self.i_x1    = Signal(width)
        self.i_y1    = Signal(width)
        
        self.i_start = Signal() # Start processing line
        self.i_next  = Signal() # Advance to next pixel

        # Output pixel coordinates
        self.o_x     = Signal(width)
        self.o_y     = Signal(width)
        
        self.o_valid = Signal() # Output pixel coordinates are valid
        self.o_last  = Signal() # Last pixel of the line

        self.r_steep = Signal() # True if line is transposed due to being steep (dy > dx)

        # Internal line coordinates; may be transposed due to line quadrant.
        self.r_x0    = Signal.like(self.i_x0)
        self.r_y0    = Signal.like(self.i_y0)
        self.r_x1    = Signal.like(self.i_x1)
        self.r_y1    = Signal.like(self.i_y1)

        # Absolute change in X and Y.
        self.r_dx    = Signal.like(self.i_x0)
        self.r_dy    = Signal.like(self.i_y0)

        self.r_error = Signal.like(self.i_y0)
        self.r_y_inc = Signal((width, True))

    def elaborate(self, platform):
        m = Module()

        with m.FSM() as fsm:
            with m.State("START"):
                # Reset output signals
                m.d.sync += [
                    self.o_valid.eq(0),
                    self.o_last.eq(0)
                ]

                with m.If(self.i_start):
                    # Transpose the coordinates so we're always in the positive X and Y quadrant.
                    dx = Signal((self.width, True))
                    dy = Signal((self.width, True))
                    m.d.comb += [
                        dx.eq(self.i_x0 - self.i_x1),
                        dy.eq(self.i_y0 - self.i_y1)
                    ]

                    abs_dx = Signal(self.width)
                    abs_dy = Signal(self.width)
                    m.d.comb += [
                        abs_dx.eq(Mux(dx < 0, -dx, dx)),
                        abs_dy.eq(Mux(dy < 0, -dy, dy))
                    ]

                    # Transpose if the angle is steep.
                    steep = Signal()
                    x0 = Signal(self.width)
                    y0 = Signal(self.width)
                    x1 = Signal(self.width)
                    y1 = Signal(self.width)
                    m.d.comb += [
                        steep.eq(abs_dx < abs_dy),
                        x0.eq(Mux(steep, self.i_y0, self.i_x0)),
                        y0.eq(Mux(steep, self.i_x0, self.i_y0)),
                        x1.eq(Mux(steep, self.i_y1, self.i_x1)),
                        y1.eq(Mux(steep, self.i_x1, self.i_y1))
                    ]
                    m.d.sync += self.r_steep.eq(steep)

                    # (x0, y0) should be the bottom left coordinate.
                    flip = Signal()
                    m.d.comb += flip.eq(x1 < x0)
                    m.d.sync += [
                        self.r_x0.eq(Mux(flip, x1, x0)),
                        self.r_y0.eq(Mux(flip, y1, y0)),
                        self.r_x1.eq(Mux(flip, x0, x1)),
                        self.r_y1.eq(Mux(flip, y0, y1))
                    ]

                    m.d.sync += [
                        self.r_dx.eq(abs_dx),
                        self.r_dy.eq(abs_dy),

                        self.r_error.eq(0),
                        self.r_y_inc.eq(Mux((~flip & (y0 < y1)) | (flip & (y1 < y0)), +self.one, -self.one))
                    ]

                    m.next = "NEXT-PIXEL"

            with m.State("NEXT-PIXEL"):
                # Output current coordinates
                m.d.sync += [
                    self.o_x.eq(Mux(self.r_steep, self.r_y0, self.r_x0)),
                    self.o_y.eq(Mux(self.r_steep, self.r_x0, self.r_y0)),
                    self.o_valid.eq(1),
                    self.o_last.eq(self.r_x0 >= self.r_x1)
                ]

                # Calculate next coordinates
                error = Signal(self.width)
                m.d.comb += error.eq(self.r_error + self.r_dy << 1)

                m.d.sync += [
                    self.r_x0.eq(self.r_x0 + self.one),
                ]

                # If error goes above threshold, update Y
                with m.If(error > self.r_dx):
                    m.d.sync += [
                        self.r_y0.eq(self.r_y0 + self.r_y_inc),
                        self.r_error.eq(error - (self.r_dx << 1))
                    ]
                with m.Else():
                    m.d.sync += [
                        self.r_error.eq(error)
                    ]

                with m.If(self.o_last):
                    m.next = "FINISH"
                with m.Else():
                    m.next = "WAIT"
                
            # Wait for pixel acknowledgement before continuing.
            with m.State("WAIT"):
                with m.If(self.i_next):
                    m.next = "NEXT-PIXEL"

            # Wait for pixel acknowledgement before resetting.
            with m.State("FINISH"):
                with m.If(self.i_next):
                    m.next = "START"

        return m


if __name__ == "__main__":
    dda = Bresenham(12, 4)
    ports = [
        dda.i_x0, dda.i_y0, dda.i_x1, dda.i_y1,
        dda.i_start, dda.i_next,
        dda.o_x, dda.o_y,
        dda.o_valid, dda.o_last
    ]

    print(verilog.convert(dda, ports=ports))

    def line_test(start, end, points):
        # Setup: draw a line from (0, 0) to (0, 10)
        yield dda.i_x0.eq(start[0])
        yield dda.i_y0.eq(start[1])
        yield dda.i_x1.eq(end[0])
        yield dda.i_y1.eq(end[1])
        yield dda.i_start.eq(1)
        yield dda.i_next.eq(0)
        
        # Wait for setup
        yield; yield
        yield dda.i_start.eq(0)
        yield; yield

        assert (yield dda.o_valid)

        for p in points:
            o_x = yield dda.o_x
            o_y = yield dda.o_y
            o_last_pixel = yield dda.o_last

            assert (o_x, o_y) == p

            yield dda.i_next.eq(1)
            yield; yield
            yield dda.i_next.eq(0)
            yield; yield

    def line45():
        yield from line_test(
            start=(0, 0),
            end=(10 << 4, 10 << 4),
            points=[
                (0 << 4, 0 << 4),
                (1 << 4, 1 << 4),
                (2 << 4, 2 << 4),
                (3 << 4, 3 << 4),
                (4 << 4, 4 << 4),
                (5 << 4, 5 << 4),
                (6 << 4, 6 << 4),
                (7 << 4, 7 << 4),
                (8 << 4, 8 << 4),
                (9 << 4, 9 << 4),
                (10 << 4, 10 << 4)
            ]
        )

    def line135():
        yield from line_test(
            start=(0 << 4, 10 << 4),
            end=(10 << 4, 0 << 4),
            points=[
                (0 << 4, 10 << 4),
                (1 << 4, 9 << 4),
                (2 << 4, 8 << 4),
                (3 << 4, 7 << 4),
                (4 << 4, 6 << 4),
                (5 << 4, 5 << 4),
                (6 << 4, 4 << 4),
                (7 << 4, 3 << 4),
                (8 << 4, 2 << 4),
                (9 << 4, 1 << 4),
                (10 << 4, 0 << 4)
            ]
        )

    def line225():
        yield from line_test(
            start=(10 << 4, 10 << 4),
            end=(0 << 4, 0 << 4),
            points=[
                (0 << 4, 0 << 4),
                (1 << 4, 1 << 4),
                (2 << 4, 2 << 4),
                (3 << 4, 3 << 4),
                (4 << 4, 4 << 4),
                (5 << 4, 5 << 4),
                (6 << 4, 6 << 4),
                (7 << 4, 7 << 4),
                (8 << 4, 8 << 4),
                (9 << 4, 9 << 4),
                (10 << 4, 10 << 4)
            ]
        )

    def line315():
        yield from line_test(
            start=(10 << 4, 0 << 4),
            end=(0 << 4, 10 << 4),
            points=[
                (0 << 4, 10 << 4),
                (1 << 4, 9 << 4),
                (2 << 4, 8 << 4),
                (3 << 4, 7 << 4),
                (4 << 4, 6 << 4),
                (5 << 4, 5 << 4),
                (6 << 4, 4 << 4),
                (7 << 4, 3 << 4),
                (8 << 4, 2 << 4),
                (9 << 4, 1 << 4),
                (10 << 4, 0 << 4)
            ]
        )

    with pysim.Simulator(dda) as sim:
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

    print("/*** TESTS PASSED ***/")
