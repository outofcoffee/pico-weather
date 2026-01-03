import framebuf

from display import DisplayWrapper
from font_renderer import FontRenderer, FontSize


class DisplayController:
    """
    Controller for the e-ink display.
    """

    RENDER_FLAG_CLEAR = 1  # 2^0
    RENDER_FLAG_APPEND_ONLY = 2  # 2^1
    RENDER_FLAG_FLUSH = 4  # 2^2
    RENDER_FLAG_THIN_PADDING = 8  # 2^3
    RENDER_FLAG_BLANK = 16  # 2^4
    RENDER_FLAG_NO_V_CURSOR = 32  # 2^5

    last_text_y = 0

    def __init__(self, epd: DisplayWrapper, font_renderer: FontRenderer = None):
        self.epd = epd
        self.font_renderer = font_renderer  # Will be set during init()

    def init(self):
        """
        Initializes the display.
        """
        # font_renderer should be injected before calling init()
        if self.font_renderer is None:
            raise ValueError("font_renderer must be set before calling init()")

    def get_last_text_y(self) -> int:
        """
        Returns the most recent Y value for rendered text
        """
        return self.last_text_y

    def get_max_line_length(self) -> int:
        """
        Returns the maximum number of characters that can fit on a line.
        """
        char_width = self.font_renderer.get_text_width("W", FontSize.SMALL)
        return self.epd.max_draw_width // char_width

    def display_text(self, render_flags: int, font_size: int, *lines: str):
        """
        Displays the given lines of text on the e-ink display, optionally appending to the existing display.
        """
        self.display_text_at_coordinates(render_flags, 0, font_size, *lines)

    def display_text_at_coordinates(self, render_flags: int, x: int, font_size: int, *lines: str):
        """
        Displays the given lines of text at specified coordinates.
        """
        if render_flags & self.RENDER_FLAG_CLEAR:
            self.epd.Clear()
        if render_flags & self.RENDER_FLAG_BLANK:
            self.epd.fill(0xff)
            self.last_text_y = self.epd.draw_start_y

        font_height = self.font_renderer.get_font_height(font_size)

        for line in lines:
            # Render the line at current position
            self.font_renderer.set_position(x, self.last_text_y)
            self.font_renderer.render_text(line, font_size)

            # Advance cursor for next line (unless NO_V_CURSOR flag is set)
            if not (render_flags & self.RENDER_FLAG_NO_V_CURSOR):
                if render_flags & self.RENDER_FLAG_THIN_PADDING:
                    line_stride = font_height + 2
                else:
                    line_stride = font_height + 4
                self.last_text_y += line_stride

        if render_flags & self.RENDER_FLAG_FLUSH:
            self.epd.display()

    def flush_display(self):
        """
        Flushes the display buffer to the display.
        """
        self.epd.display()

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
        self.add_vertical_space(4)
        self.epd.hline(1, self.last_text_y, self.epd.max_draw_width, 0x00)
        self.add_vertical_space(4)

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

    def display_right(self, flags: int, font_size: int, text: str):
        """Display right-aligned text."""
        text_width = self.font_renderer.get_text_width(text, font_size)
        padding = self.epd.max_draw_width - text_width
        self.display_text_at_coordinates(
            flags | self.RENDER_FLAG_NO_V_CURSOR,
            padding,
            font_size,
            text
        )
