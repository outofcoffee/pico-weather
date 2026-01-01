from utils import Config
from display_large import EPD_7in5_B
from display_small import EPD_2in13_V3_Landscape


class DisplayWrapper:
    """Base wrapper interface for EPD displays."""

    def __init__(self):
        # Default padding preserves existing 2px right margin
        self._padding_top = 0
        self._padding_right = 2  # Preserve legacy 2px margin
        self._padding_bottom = 0
        self._padding_left = 0

    @property
    def width(self) -> int:
        """Returns the physical width of the display."""
        raise NotImplementedError

    @property
    def max_draw_width(self) -> int:
        """Returns the maximum drawable width accounting for padding."""
        return self.width - self._padding_left - self._padding_right

    def add_padding(self, top: int, right: int, bottom: int, left: int) -> None:
        """
        Sets the padding for the display. All drawing operations will be offset
        by the padding values.

        :param top: Top padding in pixels
        :param right: Right padding in pixels
        :param bottom: Bottom padding in pixels
        :param left: Left padding in pixels
        """
        self._padding_top = top
        self._padding_right = right
        self._padding_bottom = bottom
        self._padding_left = left

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
        self._text_impl(s, x + self._padding_left, y + self._padding_top, c)

    def hline(self, x: int, y: int, w: int, c: int) -> None:
        """Draws a horizontal line on the framebuffer."""
        self._hline_impl(x + self._padding_left, y + self._padding_top, w, c)

    def blit(self, fb, x: int, y: int) -> None:
        """Blits a framebuffer to the display at the specified position."""
        self._blit_impl(fb, x + self._padding_left, y + self._padding_top)

    def _text_impl(self, s: str, x: int, y: int, c: int) -> None:
        """Implementation method for text drawing."""
        raise NotImplementedError

    def _hline_impl(self, x: int, y: int, w: int, c: int) -> None:
        """Implementation method for horizontal line drawing."""
        raise NotImplementedError

    def _blit_impl(self, fb, x: int, y: int) -> None:
        """Implementation method for blitting."""
        raise NotImplementedError


class EPD_7in5_B_Wrapper(DisplayWrapper):
    """Wrapper for EPD_7in5_B that passes through all calls without change."""

    def __init__(self):
        super().__init__()
        self._epd = EPD_7in5_B()

    @property
    def width(self) -> int:
        """Returns the physical width of the display."""
        return self._epd.width

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

    def _text_impl(self, s, x, y, c):
        self._epd.imageblack.text(s, x, y, c)

    def _hline_impl(self, x, y, w, c):
        self._epd.imageblack.hline(x, y, w, c)

    def _blit_impl(self, fb, x, y):
        self._epd.imageblack.blit(fb, x, y)


class EPD_2in13_V3_Wrapper(DisplayWrapper):
    """Wrapper for EPD_2in13_V3_Landscape that adapts its interface."""

    def __init__(self):
        super().__init__()
        self._epd = EPD_2in13_V3_Landscape()

    @property
    def width(self) -> int:
        """Returns the physical width of the display."""
        return self._epd.width

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

    def _text_impl(self, s, x, y, c):
        # The small EPD IS a framebuffer
        self._epd.text(s, x, y, c)

    def _hline_impl(self, x, y, w, c):
        # The small EPD IS a framebuffer
        self._epd.hline(x, y, w, c)

    def _blit_impl(self, fb, x, y):
        # The small EPD IS a framebuffer
        self._epd.blit(fb, x, y)


def get_epd(config: Config) -> DisplayWrapper:
    """
    Factory function that returns the appropriate EPD wrapper based on config.
    Adapts different manufacturer EPD implementations to a common DisplayWrapper interface.
    """
    if config.display_size == 'large':
        return EPD_7in5_B_Wrapper()
    elif config.display_size == 'small':
        return EPD_2in13_V3_Wrapper()
    else:
        raise ValueError(f"Unsupported display_size: {config.display_size}. Must be 'large' or 'small'.")
