from display_virtual import VirtualDisplayProxy
import machine
import utime

from display import get_epd
from font_renderer import FontSize, RichTextRenderer
from images import show_image, IMAGE_DIM
from net import connect_to_network, disconnect
from render import DisplayController
from utils import format_date, read_config, wrap_text, sentence_join, Config, truncate_lines
from weather import get_img_for_title, Weather, load_cached_weather, fetch_weather, \
    cache_weather


def fetch(config: Config, display: DisplayController) -> tuple[Weather, Weather]:
    """
    First tries to load the weather from the cache. If it's not there, connects to the configured network, fetches the
    weather, disconnects, and caches the weather.
    :param config: the configuration
    :param display: the display controller
    :return: the current and daily weather
    """
    current: Weather = load_cached_weather('current', config.cache_mins)
    daily: Weather = load_cached_weather('daily', config.cache_mins)

    if all([current, daily]):
        print(f"using cached weather")
        return current, daily
    else:
        print(f"no cached weather found; fetching from remote")

    display.display_text(
        DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_FLUSH,
        FontSize.SMALL,
        f"Connecting to {config.ssid}..."
    )

    try:
        wlan, ip = connect_to_network(config.ssid, config.password)
    except KeyboardInterrupt:
        print('received keyboard interrupt when connecting to network')
        machine.reset()

    display.display_text(
        DisplayController.RENDER_FLAG_FLUSH,
        FontSize.SMALL,
        "Connected",
        f"IP: {ip}"
    )

    try:
        current, daily = fetch_weather(display, config.lat, config.lon, config.openweathermap_key)
    except Exception as e:
        print(f"error fetching weather: {e}")
        display.display_text(
            DisplayController.RENDER_FLAG_FLUSH,
            FontSize.SMALL,
            "Failed to fetch weather",
            f"Cause: {e}"
        )
        display.deep_sleep()
    finally:
        # we don't need the network anymore
        disconnect(wlan)

        if not all([current, daily]):
            print(f"Sleeping for 5 minutes then resetting the device")
            utime.sleep(300)
            machine.reset()

    cache_weather(current, 'current')
    cache_weather(daily, 'daily')

    return current, daily


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
    desc = wrap_text(weather.description, display.get_max_text_width())

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


def main():
    config = read_config()
    phy_epd = get_epd(config)

    epd = VirtualDisplayProxy(phy_epd)
    epd.init()

    # Create font renderer and inject into display controller
    font_renderer = RichTextRenderer(epd)
    display = DisplayController(epd, font_renderer)
    display.init()

    while True:
        # buffer writes to the display
        epd.set_virtual_mode(True)

        current, daily = fetch(config, display)
        render(display, current, daily)

        # flush the display
        epd.set_virtual_mode(False)

        display.deep_sleep()

        print(f'sleeping for {config.refresh_mins} minutes')
        utime.sleep(config.refresh_mins * 60)


if __name__ == '__main__':
    main()
