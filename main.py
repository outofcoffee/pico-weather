import machine
import utime
import network
import urequests as requests

from display import EPD_2in13_V3_Landscape
from images import show_image, IMAGE_DIM
from utils import format_date, read_config, wrap_text, sentence_join

MAX_TEXT_WIDTH = 30


class Weather:
    dt: int
    temp: float
    titles: list[str]
    description: str
    day_summary: list[str]

    def __init__(self, dt: int, temp: float, titles: list[str], description: str, day_summary: list[str]):
        self.dt = dt
        self.temp = temp
        self.titles = titles
        self.description = description
        self.day_summary = day_summary


last_text_y = 0


def connect_to_network() -> tuple[network.WLAN, str]:
    """Connects to the configured network and returns the WLAN client and IP address."""

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


def display_info(append: bool, *lines: str):
    """Displays the given lines of text on the e-ink display, optionally appending to the existing display."""
    display_info_at_coordinates(append, 0, *lines)


def display_info_at_coordinates(append: bool, x: int, *lines: str):
    """Displays the given lines of text on the e-ink display, optionally appending to the existing display."""

    global last_text_y
    if not append:
        epd.fill(0xff)
        last_text_y = 0

    for line in lines:
        last_text_y += 10
        epd.text(line, x, last_text_y, 0x00)

    epd.display(epd.buffer)


def fetch_weather() -> Weather:
    """
    Fetches the current weather from OpenWeatherMap and returns a Weather of
    """

    # reduce the amount of data returned by excluding minutely, hourly, and alerts
    exclude = "minutely,hourly,alerts"

    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={openweathermap_key}&exclude={exclude}"
    print(f"querying {url}")
    r = requests.get(url)
    resp: dict = r.json()
    # print(resp)
    r.close()

    current_conditions = resp['current']
    dt: int = current_conditions['dt']

    (temp, titles, description) = summarise_conditions('current', current_conditions)

    daily_conditions = resp['daily']
    if len(daily_conditions) > 0:
        day_summary = wrap_text(daily_conditions[0]['summary'], MAX_TEXT_WIDTH)
    else:
        print(f"no daily weather returned")
        day_summary = []

    return Weather(dt, temp, titles, description, day_summary)


def summarise_conditions(weather_timeframe, conditions) -> tuple[float, list[str], str]:
    """Summarises the given current conditions and returns a tuple of (temp, titles, description)"""

    # convert from K to C
    temp_in_celsius: float = conditions['temp'] - 273.15

    weathers = conditions['weather']
    print(f"{len(weathers)} {weather_timeframe} weather(s): ", weathers)

    summary: tuple[float, list[str], str]
    if len(weathers) > 0:
        titles: list[str] = []
        descriptions: list[str] = []

        for i, weather in enumerate(weathers):
            titles.append(weather['main'])
            descriptions.append(weather['description'])

        summary = temp_in_celsius, titles, sentence_join(descriptions)

    else:
        print(f"no {weather_timeframe} weather returned")
        summary = temp_in_celsius, [], ""

    print(f"{weather_timeframe}: {summary}")
    return summary


def display_additional():
    epd.delay_ms(2000)
    epd.vline(5, 55, 60, 0x00)
    epd.vline(100, 55, 60, 0x00)
    epd.hline(5, 55, 95, 0x00)
    epd.hline(5, 115, 95, 0x00)
    epd.line(5, 55, 100, 115, 0x00)
    epd.line(100, 55, 5, 115, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(2000)

    epd.rect(130, 10, 40, 80, 0x00)
    epd.fill_rect(190, 10, 40, 80, 0x00)
    epd.Display_Base(epd.buffer)
    epd.delay_ms(2000)

    epd.init()
    for i in range(0, 10):
        epd.fill_rect(175, 105, 10, 10, 0xff)
        epd.text(str(i), 177, 106, 0x00)
        epd.display_Partial(epd.buffer)
    print("sleep")

    epd.init()
    epd.Clear()
    epd.delay_ms(2000)
    epd.sleep()


def add_vertical_space(pixels: int):
    global last_text_y
    last_text_y += pixels


def connect_and_fetch():
    """Connects to the configured network and fetches the current weather."""

    print(f"connecting to {ssid}...")

    epd.init()
    epd.Clear()
    display_info(False, f"Connecting to {ssid}...")

    try:
        wlan, ip = connect_to_network()
    except KeyboardInterrupt:
        print('received keyboard interrupt when connecting to network')
        machine.reset()
    display_info(True, "Connected", f"IP: {ip}")

    try:
        weather = fetch_weather()
    except KeyboardInterrupt:
        print('received keyboard interrupt when fetching weather')
        machine.reset()

    weather_date = format_date(weather.dt)
    display_info(
        False,
        f"Weather {weather_date}",
    )
    add_vertical_space(5)

    image_x = 0
    image_y = last_text_y + 7

    for title in weather.titles:
        img_path = get_img_for_title(title)
        if img_path:
            show_image(epd, img_path, image_x, image_y)
            image_x += IMAGE_DIM + 4

    temp = f"{weather.temp:.1f} C"
    title = sentence_join(weather.titles)
    desc = wrap_text(weather.description, MAX_TEXT_WIDTH)

    display_info_at_coordinates(
        True,
        37,
        temp,
        title,
        *desc,
    )

    add_vertical_space(5)
    display_info(
        True,
        *weather.day_summary
    )

    # display_additional()
    epd.delay_ms(2000)
    epd.sleep()

    print('disconnecting from network')
    wlan.disconnect()
    wlan.active(False)


def get_img_for_title(title):
    # convert title to image per https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
    if title == 'Clouds' or title == 'Thunderstorm':
        img_path = 'cloud'
    elif title == 'Rain' or title == 'Drizzle':
        img_path = 'rain'
    elif title == 'Snow':
        img_path = 'snow'
    elif title == 'Clear':
        img_path = 'sun'
    elif title == 'Wind':
        img_path = 'wind'
    else:
        print(f"unknown weather.title: {title}")
        img_path = None
    return img_path


if __name__ == '__main__':
    ssid, password, lat, lon, openweathermap_key, sleep_mins = read_config()
    epd = EPD_2in13_V3_Landscape()

    while True:
        connect_and_fetch()
        print(f'sleeping for {sleep_mins} minutes')
        utime.sleep(sleep_mins * 60)
