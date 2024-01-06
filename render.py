from display import EPD_2in13_V3_Landscape

MAX_TEXT_WIDTH = 30
last_text_y = 0

RENDER_FLAG_CLEAR = 1  # 2^0
RENDER_FLAG_APPEND_ONLY = 2  # 2^1
RENDER_FLAG_FLUSH = 4  # 2^2
RENDER_FLAG_THIN_PADDING = 8  # 2^3
RENDER_FLAG_BLANK = 16  # 2^4


def get_last_text_y() -> int:
    """
    Returns the most recent Y value for rendered text
    """
    return last_text_y


def display_text(epd: EPD_2in13_V3_Landscape, render_flags: int, *lines: str):
    """
    Displays the given lines of text on the e-ink display, optionally appending to the existing display.
    """
    display_text_at_coordinates(epd, render_flags, 0, *lines)


def display_text_at_coordinates(epd: EPD_2in13_V3_Landscape, render_flags: int, x: int, *lines: str):
    """
    Displays the given lines of text on the e-ink display, optionally appending to the existing display.
    """
    global last_text_y

    if render_flags & RENDER_FLAG_CLEAR:
        epd.Clear()
    if render_flags & RENDER_FLAG_BLANK:
        epd.fill(0xff)
        last_text_y = 0

    for line in lines:
        if render_flags & RENDER_FLAG_THIN_PADDING:
            line_stride = 8
        else:
            line_stride = 10

        last_text_y += line_stride
        epd.text(line, x, last_text_y, 0x00)

    if render_flags & RENDER_FLAG_FLUSH:
        epd.display(epd.buffer)


def flush_display(epd: EPD_2in13_V3_Landscape):
    """
    Flushes the display buffer to the display.
    :param epd: the display
    """
    epd.display(epd.buffer)


def add_vertical_space(pixels: int):
    """
    Adds the given number of pixels of vertical space to the display.
    :param pixels: the number of pixels
    """
    global last_text_y
    last_text_y += pixels


def render_horizontal_separator(epd: EPD_2in13_V3_Landscape):
    """
    Renders a horizontal separator on the display.
    """
    add_vertical_space(2)
    epd.hline(1, get_last_text_y() + 8, 248, 0x00)
    add_vertical_space(2)
