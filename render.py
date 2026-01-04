from display import DisplayController
from font_renderer import FontSize
from images import IMAGE_DIM, show_image
from utils import format_date, sentence_join, truncate_lines, wrap_text
from weather import Weather, get_img_for_title


def render_weather(display: DisplayController, weather: Weather, show_min_max: bool = False):
    """
    Renders the given weather on the display.
    :param display: the display controller
    :param weather: the weather
    :param show_min_max: whether to show the min/max temperatures
    """
    image_x = 0
    image_y = display.get_last_text_y() + 7

    # Render weather icons (unchanged)
    img_paths = []
    for title in weather.titles:
        img_path = get_img_for_title(title)
        if img_path:
            img_paths.append(img_path)

    for img_path in set(img_paths):
        show_image(display, img_path, image_x, image_y)
        image_x += IMAGE_DIM + 4

    temp = f"{weather.temp.main:.1f}°C"  # Use degree symbol
    title = sentence_join(weather.titles)
    desc = wrap_text(weather.description, display.get_max_line_length())

    # LARGE font (24px) for temperature
    display.display_text_at_coordinates(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        image_x,
        FontSize.LARGE,
        temp,
    )

    if show_min_max:
        min_max = f"L/H: {weather.temp.temp_min:.1f}-{weather.temp.temp_max:.1f}°C"
        display.display_right(
            DisplayController.RENDER_FLAG_APPEND_ONLY,
            FontSize.SMALL,
            min_max
        )

    # SMALL font for title and description
    display.display_text_at_coordinates(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        image_x,
        FontSize.SMALL,
        title,
        *desc,
    )


def render(display: DisplayController, current: Weather, daily: Weather):
    """
    Renders the given weather on the display.
    :param display: the display controller
    :param current: the current weather
    :param daily: the daily weather
    """
    weather_date = format_date(current.dt)

    # MEDIUM font (20px) for "NOW" header
    display.display_text(
        DisplayController.RENDER_FLAG_CLEAR | DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_THIN_PADDING,
        FontSize.MEDIUM,
        "NOW"
    )

    # Right-align date with SMALL font (18px)
    display.display_right(
        DisplayController.RENDER_FLAG_APPEND_ONLY | DisplayController.RENDER_FLAG_NO_V_CURSOR,
        FontSize.SMALL,
        weather_date
    )

    render_weather(display, current)

    display.render_horizontal_separator()

    # MEDIUM font for "TODAY" header
    display.display_text(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        FontSize.MEDIUM,
        "TODAY"
    )
    display.add_vertical_space(2)

    # SMALL font for body text
    today_summary = truncate_lines(daily.day_summary, 3)
    display.display_text(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        FontSize.SMALL,
        *today_summary
    )
    display.add_vertical_space(4)
    render_weather(display, daily, show_min_max=True)

    display.flush_display()