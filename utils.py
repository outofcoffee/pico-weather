import utime
import sys
import os


def format_date(dt: int) -> str:
    """Converts a unix timestamp to a string like "1 Jan 12:34\""""

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

    return f"{dtup[2]} {formatted} {dtup[3]:02d}:{dtup[4]:02d}"


def wrap_text(text: str, max_width: int) -> list[str]:
    return [text[idx:idx + max_width] for idx in range(0, len(text), max_width)]


def read_config() -> tuple[str, str, str, str, str, int]:
    """Reads the configuration file and returns a tuple of (ssid, password, lat, lon, openweathermap_key, sleep_mins)"""

    global ssid, password, lat, lon, openweathermap_key, sleep_mins
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
            elif line.startswith('sleep_mins='):
                sleep_mins = int(line[11:].strip())

    return ssid, password, lat, lon, openweathermap_key, sleep_mins
