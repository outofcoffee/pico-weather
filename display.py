from utils import Config
from display_large import EPD_7in5_B
from display_small import EPD_2in13_V3_Landscape


class DisplayWrapper:
    """Base wrapper interface for EPD displays."""

    def init(self):
        raise NotImplementedError

    def Clear(self):
        raise NotImplementedError

    def display(self):
        raise NotImplementedError

    def delay_ms(self, ms):
        raise NotImplementedError

    def sleep(self):
        raise NotImplementedError

    def fill(self, color):
        raise NotImplementedError

    def text(self, s, x, y, c):
        raise NotImplementedError

    def hline(self, x, y, w, c):
        raise NotImplementedError

    def blit(self, fb, x, y):
        raise NotImplementedError


class EPD_7in5_B_Wrapper(DisplayWrapper):
    """Wrapper for EPD_7in5_B that passes through all calls without change."""

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
