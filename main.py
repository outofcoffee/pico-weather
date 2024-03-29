import machine
import utime

from display import EPD_2in13_V3_Landscape
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
        f"Connecting to {config.ssid}..."
    )

    try:
        wlan, ip = connect_to_network(config.ssid, config.password)
    except KeyboardInterrupt:
        print('received keyboard interrupt when connecting to network')
        machine.reset()

    display.display_text(
        DisplayController.RENDER_FLAG_FLUSH,
        "Connected",
        f"IP: {ip}"
    )

    try:
        current, daily = fetch_weather(config.lat, config.lon, config.openweathermap_key)
    except Exception as e:
        print(f"error fetching weather: {e}")
        display.display_text(
            DisplayController.RENDER_FLAG_FLUSH,
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

    display.display_text(
        DisplayController.RENDER_FLAG_CLEAR | DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_THIN_PADDING,
        "NOW"
    )
    display.display_right(
        DisplayController.RENDER_FLAG_APPEND_ONLY | DisplayController.RENDER_FLAG_NO_V_CURSOR,
        weather_date
    )
    render_weather(display, current)

    display.render_horizontal_separator()
    display.display_text(DisplayController.RENDER_FLAG_APPEND_ONLY, "TODAY")
    display.add_vertical_space(2)

    today_summary = truncate_lines(daily.day_summary, 3)
    display.display_text(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
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

    img_paths = []
    for title in weather.titles:
        img_path = get_img_for_title(title)
        if img_path:
            img_paths.append(img_path)

    for img_path in set(img_paths):
        show_image(display, img_path, image_x, image_y)
        image_x += IMAGE_DIM + 4

    temp = f"{weather.temp.main:.1f} C"
    title = sentence_join(weather.titles)
    desc = wrap_text(weather.description, DisplayController.MAX_TEXT_WIDTH)

    # render to the right of the image (image_x)
    display.display_text_at_coordinates(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        image_x,
        temp,
    )

    if show_min_max:
        display.display_right(
            DisplayController.RENDER_FLAG_APPEND_ONLY,
            f"L/H: {weather.temp.temp_min:.1f}-{weather.temp.temp_max:.1f} C"
        )

    display.display_text_at_coordinates(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        image_x,
        title,
        *desc,
    )


def main():
    config = read_config()
    epd = EPD_2in13_V3_Landscape()
    display = DisplayController(epd)

    while True:
        display.init()
        current, daily = fetch(config, display)
        render(display, current, daily)
        display.deep_sleep()

        print(f'sleeping for {config.refresh_mins} minutes')
        utime.sleep(config.refresh_mins * 60)


if __name__ == '__main__':
    main()
