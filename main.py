import machine
import utime
import network
import urequests as requests

from display import EPD_2in13_V3_Landscape

def read_config():
    """Reads the configuration file and returns a tuple of (ssid, password, lat, lon, openweathermap_key)"""

    global ssid, password, lat, lon, openweathermap_key
    with open('config.txt') as f:
        for line in f:
            if line.startswith('ssid='):
                ssid = line[5:].strip()
            elif line.startswith('password='):
                password = line[9:].strip()
            elif line.startswith('lat='):
                lat = line[4:].strip()
            elif line.startswith('lon='):
                lon = line[4:].strip()
            elif line.startswith('openweathermap_key='):
                openweathermap_key = line[19:].strip()

    return ssid, password, lat, lon, openweathermap_key


last_text_y = 0

def connect_to_network() -> str:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        utime.sleep(1)
    ifconfig = wlan.ifconfig()
    print(ifconfig)

    # return IP address
    ip_addr = ifconfig[0]
    print(f'Connected on {ip_addr}')
    return ip_addr


def display_info(append: bool = False, line1: str = "", line2: str = "", line3: str = "", line4: str = ""):
    global last_text_y
    if not append:
        epd.fill(0xff)
        last_text_y = 0

    append_text(line1)
    append_text(line2)
    append_text(line3)
    append_text(line4)

    epd.display(epd.buffer)
    epd.delay_ms(2000)


def append_text(text: str):
    global last_text_y
    last_text_y += 10
    epd.text(text, 0, last_text_y, 0x00)


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


def fetch_weather() -> tuple[int, str, str, str]:
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={openweathermap_key}"
    print(f"querying {url}")
    r = requests.get(url)
    resp: dict = r.json()
    # print(resp)
    r.close()

    current_conditions = resp['current']

    dt = current_conditions['dt']

    # convert from K to C
    temp = current_conditions['temp'] - 273.15
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


def format_date(dt: int) -> str:
    dtup = utime.localtime(dt)
    formatted: str
    if dtup[1] == 1:
        formatted = "Jan"
    elif dtup[1] == 2:
        formatted = "Feb"
    elif dtup[1] == 3:
        formatted = "Mar"
    elif dtup[1] == 4:
        formatted = "Apr"
    elif dtup[1] == 5:
        formatted = "May"
    elif dtup[1] == 6:
        formatted = "Jun"
    elif dtup[1] == 7:
        formatted = "Jul"
    elif dtup[1] == 8:
        formatted = "Aug"
    elif dtup[1] == 9:
        formatted = "Sep"
    elif dtup[1] == 10:
        formatted = "Oct"
    elif dtup[1] == 11:
        formatted = "Nov"
    elif dtup[1] == 12:
        formatted = "Dec"
    else:
        formatted = "???"

    return f"{dtup[2]} {formatted}"


if __name__ == '__main__':
    ssid, password, lat, lon, openweathermap_key = read_config()

    epd = EPD_2in13_V3_Landscape()
    epd.Clear()

    display_info(False, f"Connecting to {ssid}...")

    try:
        ip = connect_to_network()
    except KeyboardInterrupt:
        print('received keyboard interrupt when connecting to network')
        machine.reset()

    display_info(True, "Connected to", ssid, "IP:", ip)

    try:
        weather = fetch_weather()
    except KeyboardInterrupt:
        print('received keyboard interrupt when fetching weather')
        machine.reset()

    weather_date = format_date(weather[0])
    display_info(False, f"Weather {weather_date}", weather[1], weather[2], weather[3])

    # display_additional()
