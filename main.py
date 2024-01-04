import machine
import utime
import network
import urequests as requests
import framebuf

from display import EPD_2in13_V3_Landscape
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


def show_image(img_path: str):
    fb: framebuf.FrameBuffer
    if img_path == 'cloud':
        fb = framebuf.FrameBuffer(bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xaf\xff\xff\xfe\x01\xff\xff\xf8\x00\xff\xff\xf0\x00\x7f\xff\x60\x00\x3f\xfc\x00\x00\x3f\xf8\x00\x00\x1f\xf0\x00\x00\x1f\xf0\x00\x00\x1f\xc0\x00\x00\x0f\xc0\x00\x00\x03\x80\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x01\xc0\x00\x00\x01\xe0\x00\x00\x07\xfa\xa9\x52\xaf\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'), 32, 32, framebuf.MONO_HLSB)

    elif img_path == 'rain':
        fb = framebuf.FrameBuffer(bytearray(
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x8f\xff\xff\xfe\x01\xff\xff\xf8\x00\xff\xff\xd0\x00\xff\xff\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x3f\xfc\x00\x00\x3f\xf0\x00\x00\x0f\xe0\x00\x00\x07\xe0\x00\x00\x07\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xe0\x00\x00\x07\xe0\x00\x00\x07\xf8\x00\x00\x1f\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xee\x67\x7f\xfc\x66\x66\x3f\xfc\xc6\x66\x7f\xfe\x66\x67\x3f\xfe\xe6\x67\x7f\xff\xe6\xe7\xff\xff\xef\xf7\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
                                  32, 32, framebuf.MONO_HLSB)

    elif img_path == 'snow':
        fb = framebuf.FrameBuffer(bytearray(
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xe2\x47\xff\xff\xf0\x0f\xff\xff\x38\x1c\xff\xff\x3c\x3c\xff\xf9\x3e\x7c\x9f\xf8\x1e\x78\x1f\xfe\x1e\x78\x7f\xf8\x0e\x70\x1f\xf0\x42\x42\x0f\xff\xf0\x0f\xdf\xff\xf8\x1f\xff\xff\xf8\x1f\xff\xfb\xe0\x0f\xdf\xf0\x06\x40\x0f\xfc\x0e\x70\x3f\xfc\x1e\x78\x7f\xf8\x3e\x7c\x1f\xf9\x3e\x7c\x9f\xff\x3c\x3c\xff\xff\x38\x1c\xff\xff\xf0\x0f\xff\xff\xe2\x4f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
                                  32, 32, framebuf.MONO_HLSB)

    elif img_path == 'sun':
        fb = framebuf.FrameBuffer(bytearray(
            b'\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfc\x3f\xff\xff\xfe\x7f\xff\xfb\xff\xff\xdf\xf1\xff\xff\x8f\xf8\xff\xff\x1f\xfc\xf0\x0f\x3f\xff\xc0\x03\xff\xff\x80\x01\xff\xff\x00\x01\xff\xff\x00\x00\xff\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xde\x00\x00\x7b\x0e\x00\x00\x70\x0e\x00\x00\x70\xde\x00\x00\x7b\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xff\x00\x00\xff\xff\x80\x01\xff\xff\x80\x01\xff\xff\xe0\x07\xff\xfc\xf0\x1f\x3f\xf0\xff\xff\x0f\xf1\xff\xff\x8f\xfb\xff\xff\x9f\xff\xfe\x7f\xff\xff\xfc\x3f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff'),
                                  32, 32, framebuf.MONO_HLSB)

    elif img_path == 'wind':
        fb = framebuf.FrameBuffer(bytearray(
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xbf\xff\xff\xfc\x0f\xff\xff\xf8\x07\xfe\xff\xf8\xc3\xf0\x1f\xf9\xf1\xe0\x0f\xff\xf1\xc3\x87\xff\xf3\xc7\xe3\xff\xf1\xef\xe3\xff\xc3\xff\xf3\xc0\x07\xff\xe3\xc0\x0f\xff\xe3\xea\xbf\xff\xc7\xff\xf6\xfe\x87\xc0\x00\x00\x0f\xc0\x00\x00\x3f\xff\xff\xff\xff\xe0\x02\x7f\xff\xc0\x00\x1f\xff\xc0\x00\x0f\xff\xff\xff\x8f\xff\xff\xff\xc7\xff\xff\xff\xc7\xff\xff\xff\xe7\xff\xff\xe7\xc7\xff\xff\xe3\x0f\xff\xff\xf0\x0f\xff\xff\xf8\x3f\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
                                  32, 32, framebuf.MONO_HLSB)

    else:
        print(f"unknown image path {img_path}")
        return

    epd.blit(fb, 0, 50)
    epd.display(epd.buffer)


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
        show_image('cloud')
    elif weather[2] == 'Rain' or weather[2] == 'Drizzle':
        show_image('rain')
    elif weather[2] == 'Snow':
        show_image('snow')
    elif weather[2] == 'Clear':
        show_image('sun')
    elif weather[2] == 'Wind':
        show_image('wind')

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
