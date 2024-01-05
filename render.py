from display import EPD_2in13_V3_Landscape

MAX_TEXT_WIDTH = 30
last_text_y = 0


def display_info(epd: EPD_2in13_V3_Landscape, append: bool, *lines: str):
    """
    Displays the given lines of text on the e-ink display, optionally appending to the existing display.
    """
    display_info_at_coordinates(epd, append, 0, *lines)


def display_info_at_coordinates(epd: EPD_2in13_V3_Landscape, append: bool, x: int, *lines: str):
    """
    Displays the given lines of text on the e-ink display, optionally appending to the existing display.
    """
    global last_text_y
    if not append:
        epd.fill(0xff)
        last_text_y = 0

    for line in lines:
        last_text_y += 10
        epd.text(line, x, last_text_y, 0x00)

    epd.display(epd.buffer)


def add_vertical_space(pixels: int):
    """
    Adds the given number of pixels of vertical space to the display.
    :param pixels: the number of pixels
    """
    global last_text_y
    last_text_y += pixels
