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


def display_info(line1: str, line2: str = "", line3: str = "", line4: str = ""):
    epd.Clear()

    epd.fill(0xff)
    epd.text(line1, 0, 10, 0x00)
    epd.text(line2, 0, 20, 0x00)
    epd.text(line3, 0, 30, 0x00)
    epd.text(line4, 0, 40, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(150)


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


def fetch_weather() -> str:
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={openweathermap_key}"
    print(f"querying {url}")
    r = requests.get(url)
    resp: dict = r.json()
    print(resp)
    r.close()

    current_conditions = resp['current']

    # convert from K to C
    temp = current_conditions['temp'] -273.15
    current_weather = current_conditions['weather']

    summary = f"{current_weather['main']} ({temp}) {current_weather['description']}"
    print(summary)
    return summary


if __name__ == '__main__':
    ssid, password, lat, lon, openweathermap_key = read_config()

    epd = EPD_2in13_V3_Landscape()

    display_info(f"Connecting to {ssid}...")

    try:
        ip = connect_to_network()
    except KeyboardInterrupt:
        print('received keyboard interrupt when connecting to network')
        machine.reset()

    display_info("Connected to", ssid, "IP:", ip)

    try:
        weather = fetch_weather()
    except KeyboardInterrupt:
        print('received keyboard interrupt when fetching weather')
        machine.reset()

    display_info("Weather", weather, "", "")

    display_additional()
