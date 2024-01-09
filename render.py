import framebuf

from display import EPD_2in13_V3_Landscape


class DisplayController:
    """
    Controller for the e-ink display.
    """

    MAX_TEXT_WIDTH = 30

    RENDER_FLAG_CLEAR = 1  # 2^0
    RENDER_FLAG_APPEND_ONLY = 2  # 2^1
    RENDER_FLAG_FLUSH = 4  # 2^2
    RENDER_FLAG_THIN_PADDING = 8  # 2^3
    RENDER_FLAG_BLANK = 16  # 2^4

    last_text_y = 0

    def __init__(self, epd: EPD_2in13_V3_Landscape):
        self.epd = epd

    def init(self):
        """
        Initializes the display.
        """
        self.epd.init()

    def get_last_text_y(self) -> int:
        """
        Returns the most recent Y value for rendered text
        """
        return self.last_text_y

    def display_text(self, render_flags: int, *lines: str):
        """
        Displays the given lines of text on the e-ink display, optionally appending to the existing display.
        """
        self.display_text_at_coordinates(render_flags, 0, *lines)

    def display_text_at_coordinates(self, render_flags: int, x: int, *lines: str):
        """
        Displays the given lines of text on the e-ink display, optionally appending to the existing display.
        """
        if render_flags & self.RENDER_FLAG_CLEAR:
            self.epd.Clear()
        if render_flags & self.RENDER_FLAG_BLANK:
            self.epd.fill(0xff)
            self.last_text_y = 0

        for line in lines:
            if render_flags & self.RENDER_FLAG_THIN_PADDING:
                line_stride = 8
            else:
                line_stride = 10

            self.last_text_y += line_stride
            self.epd.text(line, x, self.last_text_y, 0x00)

        if render_flags & self.RENDER_FLAG_FLUSH:
            self.epd.display(self.epd.buffer)

    def flush_display(self):
        """
        Flushes the display buffer to the display.
        :param epd: the display
        """
        self.epd.display(self.epd.buffer)

    def add_vertical_space(self, pixels: int):
        """
        Adds the given number of pixels of vertical space to the display.
        :param pixels: the number of pixels
        """
        self.last_text_y += pixels

    def render_horizontal_separator(self):
        """
        Renders a horizontal separator on the display.
        """
        self.add_vertical_space(2)
        self.epd.hline(1, self.get_last_text_y() + 8, 248, 0x00)
        self.add_vertical_space(2)

    def deep_sleep(self):
        """
        Puts the display into deep sleep mode, pausing first.
        """
        self.epd.delay_ms(2000)
        self.epd.sleep()

    def blit(self, fb: framebuf.FrameBuffer, x: int, y: int):
        """
        Blits the given framebuffer to the display at the given coordinates.
        :param fb: the framebuffer
        :param x: x coordinate
        :param y: y coordinate
        """
        self.epd.blit(fb, x, y)
