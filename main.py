import machine
import utime
import network

from display import EPD_2in13_V3_Landscape
from images import show_image, IMAGE_DIM
from render import MAX_TEXT_WIDTH, display_text, display_text_at_coordinates, add_vertical_space, \
    get_last_text_y, flush_display, RENDER_FLAG_FLUSH, RENDER_FLAG_CLEAR, RENDER_FLAG_APPEND_ONLY, \
    render_horizontal_separator, RENDER_FLAG_THIN_PADDING, RENDER_FLAG_BLANK
from utils import format_date, read_config, wrap_text, sentence_join, Config
from weather import get_img_for_title, fetch_weather, Weather


def connect_to_network(ssid: str, password: str) -> tuple[network.WLAN, str]:
    """
    Connects to the configured network and returns the WLAN client and IP address.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        utime.sleep(1)

    ifconfig = wlan.ifconfig()
    print(ifconfig)

    ip_addr = ifconfig[0]
    print(f'Connected on {ip_addr}')
    return wlan, ip_addr


def disconnect(wlan: network.WLAN):
    """
    Disconnects from the given WLAN client.
    """
    print('disconnecting from network')
    wlan.disconnect()
    wlan.active(False)


def connect_and_fetch(config: Config, epd: EPD_2in13_V3_Landscape):
    """
    Connects to the configured network and fetches the current weather.
    :param config: the configuration
    :param epd: the e-ink display
    """
    print(f"connecting to {config.ssid}...")

    epd.init()

    display_text(
        epd,
        RENDER_FLAG_BLANK | RENDER_FLAG_FLUSH,
        f"Connecting to {config.ssid}..."
    )

    try:
        wlan, ip = connect_to_network(config.ssid, config.password)
    except KeyboardInterrupt:
        print('received keyboard interrupt when connecting to network')
        machine.reset()

    display_text(
        epd,
        RENDER_FLAG_FLUSH,
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

    display_text(
        epd,
        RENDER_FLAG_CLEAR | RENDER_FLAG_BLANK | RENDER_FLAG_THIN_PADDING,
        f"Weather {weather_date}",
    )

    render_horizontal_separator(epd)
    display_text(epd, RENDER_FLAG_APPEND_ONLY, "NOW")
    render_weather(epd, current)

    render_horizontal_separator(epd)
    display_text(epd, RENDER_FLAG_APPEND_ONLY, "TODAY")
    display_text(
        epd,
        RENDER_FLAG_APPEND_ONLY,
        *daily.day_summary
    )
    add_vertical_space(2)
    render_weather(epd, daily)

    flush_display(epd)
    epd.delay_ms(2000)
    epd.sleep()


def render_weather(epd: EPD_2in13_V3_Landscape, weather: Weather):
    image_x = 0
    image_y = get_last_text_y() + 7
    for title in weather.titles:
        img_path = get_img_for_title(title)
        if img_path:
            show_image(epd, img_path, image_x, image_y)
            image_x += IMAGE_DIM + 4

    temp = f"{weather.temp:.1f} C"
    title = sentence_join(weather.titles)
    desc = wrap_text(weather.description, MAX_TEXT_WIDTH)
    display_text_at_coordinates(
        epd,
        RENDER_FLAG_APPEND_ONLY,
        37,
        temp,
        title,
        *desc,
    )


def main():
    config = read_config()
    epd = EPD_2in13_V3_Landscape()

    while True:
        connect_and_fetch(config, epd)
        print(f'sleeping for {config.sleep_mins} minutes')
        utime.sleep(config.sleep_mins * 60)


if __name__ == '__main__':
    main()
