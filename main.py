import machine
import utime
import network
import urequests as requests

from display import EPD_2in13_V3_Landscape
from images import show_image
from utils import format_date, read_config

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

    global last_text_y
    if not append:
        epd.fill(0xff)
        last_text_y = 0

    for line in lines:
        last_text_y += 10
        epd.text(line, 0, last_text_y, 0x00)

    epd.display(epd.buffer)


def fetch_weather() -> tuple[int, str, str, str]:
    """Fetches the current weather from OpenWeatherMap and returns a tuple of (dt, temp, main, description)"""

    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={openweathermap_key}"
    print(f"querying {url}")
    r = requests.get(url)
    resp: dict = r.json()
    # print(resp)
    r.close()

    current_conditions = resp['current']

    dt = current_conditions['dt']

    # convert from K to C
    temp = f"{current_conditions['temp'] - 273.15:.1f}"
    current_weathers = current_conditions['weather']

    summary: tuple[dt, str, str, str]
    if len(current_weathers) > 0:
        current_weather = current_weathers[0]
        summary = dt, f"{temp} C", current_weather['main'], current_weather['description']
    else:
        print('no current weather returned')
        summary = dt, f"{temp} C", "", ""

    print(summary)
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

    weather_date = format_date(weather[0])
    display_info(False, f"Weather {weather_date}", weather[1], weather[2], weather[3])

    # convert weather[2] to image per https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
    if weather[2] == 'Clouds' or weather[2] == 'Thunderstorm':
        show_image(epd, 'cloud')
    elif weather[2] == 'Rain' or weather[2] == 'Drizzle':
        show_image(epd, 'rain')
    elif weather[2] == 'Snow':
        show_image(epd, 'snow')
    elif weather[2] == 'Clear':
        show_image(epd, 'sun')
    elif weather[2] == 'Wind':
        show_image(epd, 'wind')

    # display_additional()
    epd.delay_ms(2000)
    epd.sleep()

    print('disconnecting from network')
    wlan.disconnect()
    wlan.active(False)


if __name__ == '__main__':
    ssid, password, lat, lon, openweathermap_key, sleep_mins = read_config()
    epd = EPD_2in13_V3_Landscape()

    while True:
        connect_and_fetch()
        print(f'sleeping for {sleep_mins} minutes')
        utime.sleep(sleep_mins * 60)
