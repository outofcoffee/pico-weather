from epd.Pico_ePaper_7_5_B import EPD_7in5_B
from epd.Pico_ePaper_2_13_V3 import EPD_2in13_V3_Landscape


class DisplayWrapper:
    """Base wrapper interface for EPD displays."""

    @property
    def width(self) -> int:
        """Returns the physical width of the display."""
        raise NotImplementedError

    @property
    def height(self) -> int:
        """Returns the physical height of the display."""
        raise NotImplementedError

    @property
    def max_draw_width(self) -> int:
        """Returns the maximum drawable width accounting for padding."""
        return self.width

    @property
    def draw_start_y(self) -> int:
        """Returns the Y coordinate where drawing should start."""
        return 0

    def init(self) -> None:
        """Initializes the display hardware."""
        raise NotImplementedError

    def Clear(self) -> None:
        """Clears the display buffer."""
        raise NotImplementedError

    def display(self) -> None:
        """Flushes the buffer to the display."""
        raise NotImplementedError

    def delay_ms(self, ms: int) -> None:
        """Delays for the specified number of milliseconds."""
        raise NotImplementedError

    def sleep(self) -> None:
        """Puts the display into sleep mode."""
        raise NotImplementedError

    def fill(self, color: int) -> None:
        """Fills the framebuffer with the specified color."""
        raise NotImplementedError

    def text(self, s: str, x: int, y: int, c: int) -> None:
        """Draws text on the framebuffer at the specified position."""
        raise NotImplementedError

    def hline(self, x: int, y: int, w: int, c: int) -> None:
        """Draws a horizontal line on the framebuffer."""
        raise NotImplementedError

    def blit(self, fb, x: int, y: int) -> None:
        """Blits a framebuffer to the display at the specified position."""
        raise NotImplementedError

    def scroll(self, dx: int, dy: int) -> None:
        """Scrolls the framebuffer by dx, dy pixels."""
        raise NotImplementedError

    def fill_rect(self, x: int, y: int, w: int, h: int, c: int) -> None:
        """Fills a rectangle on the framebuffer."""
        raise NotImplementedError


class EPD_7in5_B_Wrapper(DisplayWrapper):
    """Wrapper for EPD_7in5_B that passes through all calls without change."""

    def __init__(self):
        self._epd = EPD_7in5_B()

    @property
    def width(self) -> int:
        """Returns the physical width of the display."""
        return self._epd.width

    @property
    def height(self) -> int:
        """Returns the physical height of the display."""
        return self._epd.height

    def init(self):
        self._epd.init()

    def Clear(self):
        self._epd.ClearBlack()

    def display(self):
        self._epd.display()

    def delay_ms(self, ms):
        self._epd.delay_ms(ms)

    def sleep(self):
        self._epd.sleep()

    def fill(self, color):
        self._epd.imageblack.fill(color)

    def text(self, s, x, y, c):
        self._epd.imageblack.text(s, x, y, c)

    def hline(self, x, y, w, c):
        self._epd.imageblack.hline(x, y, w, c)

    def blit(self, fb, x, y):
        self._epd.imageblack.blit(fb, x, y)

    def scroll(self, dx, dy):
        self._epd.imageblack.scroll(dx, dy)

    def fill_rect(self, x, y, w, h, c):
        self._epd.imageblack.fill_rect(x, y, w, h, c)


class EPD_2in13_V3_Wrapper(DisplayWrapper):
    """Wrapper for EPD_2in13_V3_Landscape that adapts its interface."""

    def __init__(self):
        self._epd = EPD_2in13_V3_Landscape()

    @property
    def width(self) -> int:
        """Returns the physical width of the display."""
        return self._epd.width

    @property
    def height(self) -> int:
        """Returns the physical height of the display."""
        return self._epd.height

    def init(self):
        self._epd.init()

    def Clear(self):
        self._epd.Clear()

    def display(self):
        # The small EPD's display() requires the buffer as a parameter
        self._epd.display(self._epd.buffer)

    def delay_ms(self, ms):
        self._epd.delay_ms(ms)

    def sleep(self):
        self._epd.sleep()

    def fill(self, color):
        # The small EPD IS a framebuffer
        self._epd.fill(color)

    def text(self, s, x, y, c):
        # The small EPD IS a framebuffer
        self._epd.text(s, x, y, c)

    def hline(self, x, y, w, c):
        # The small EPD IS a framebuffer
        self._epd.hline(x, y, w, c)

    def blit(self, fb, x, y):
        # The small EPD IS a framebuffer
        self._epd.blit(fb, x, y)

    def scroll(self, dx, dy):
        # The small EPD IS a framebuffer
        self._epd.scroll(dx, dy)

    def fill_rect(self, x, y, w, h, c):
        # The small EPD IS a framebuffer
        self._epd.fill_rect(x, y, w, h, c)
