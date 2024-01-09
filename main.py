import machine
import utime

from display import EPD_2in13_V3_Landscape
from images import show_image, IMAGE_DIM
from net import connect_to_network, disconnect
from render import DisplayController
from utils import format_date, read_config, wrap_text, sentence_join, Config
from weather import get_img_for_title, fetch_weather, Weather


def fetch_and_render(config: Config, display: DisplayController):
    """
    Connects to the configured network and fetches the current weather.
    :param config: the configuration
    :param display: the display controller
    """
    print(f"connecting to {config.ssid}...")

    display.init()

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
    except KeyboardInterrupt:
        print('received keyboard interrupt when fetching weather')
        machine.reset()

    # we don't need the network anymore
    disconnect(wlan)

    weather_date = format_date(current.dt)

    display.display_text(
        DisplayController.RENDER_FLAG_CLEAR | DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_THIN_PADDING,
        f"Weather {weather_date}",
    )

    display.render_horizontal_separator()
    display.display_text(DisplayController.RENDER_FLAG_APPEND_ONLY, "NOW")
    render_weather(display, current)

    display.render_horizontal_separator()
    display.display_text(DisplayController.RENDER_FLAG_APPEND_ONLY, "TODAY")
    display.display_text(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        *daily.day_summary
    )
    display.add_vertical_space(2)
    render_weather(display, daily)

    display.flush_display()
    display.deep_sleep()


def render_weather(display: DisplayController, weather: Weather):
    """
    Renders the given weather on the display.
    :param display: the display controller
    :param weather: the weather
    """
    image_x = 0
    image_y = display.get_last_text_y() + 7
    for title in weather.titles:
        img_path = get_img_for_title(title)
        if img_path:
            show_image(display, img_path, image_x, image_y)
            image_x += IMAGE_DIM + 4

    temp = f"{weather.temp:.1f} C"
    title = sentence_join(weather.titles)
    desc = wrap_text(weather.description, DisplayController.MAX_TEXT_WIDTH)

    # render to the right of the image (image_x)
    display.display_text_at_coordinates(
        DisplayController.RENDER_FLAG_APPEND_ONLY,
        image_x,
        temp,
        title,
        *desc,
    )


def main():
    config = read_config()
    epd = EPD_2in13_V3_Landscape()
    display = DisplayController(epd)

    while True:
        fetch_and_render(config, display)
        print(f'sleeping for {config.sleep_mins} minutes')
        utime.sleep(config.sleep_mins * 60)


if __name__ == '__main__':
    main()
