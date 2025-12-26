from utils import Config
from display_large import EPD_7in5_B
from display_small import EPD_2in13_V3_Landscape


class DisplayWrapper:
    """Base wrapper interface for EPD displays."""

    max_draw_width: int = 0  # Must be set by subclasses

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


class EPD_7in5_B_Wrapper(DisplayWrapper):
    """Wrapper for EPD_7in5_B that passes through all calls without change."""

    max_draw_width = 798  # 800px width - 2px margin

    def __init__(self):
        self._epd = EPD_7in5_B()

    def init(self):
        self._epd.init()

    def Clear(self):
        self._epd.Clear()

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


class EPD_2in13_V3_Wrapper(DisplayWrapper):
    """Wrapper for EPD_2in13_V3_Landscape that adapts its interface."""

    max_draw_width = 248  # 250px width - 2px margin

    def __init__(self):
        self._epd = EPD_2in13_V3_Landscape()

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


def get_epd(config: Config) -> DisplayWrapper:
    """
    Factory function that returns the appropriate EPD wrapper based on config.
    Adapts different manufacturer EPD implementations to a common DisplayWrapper interface.
    """
    match config.display_size:
        case 'large':
            return EPD_7in5_B_Wrapper()
        case 'small':
            return EPD_2in13_V3_Wrapper()
        case _:
            raise ValueError(f"Unsupported display_size: {config.display_size}. Must be 'large' or 'small'.")
