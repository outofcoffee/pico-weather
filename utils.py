import utime


class Config:
    ssid: str
    password: str
    lat: str
    lon: str
    openweathermap_key: str
    sleep_mins: int


def format_date(dt: int) -> str:
    """
    Converts a unix timestamp to a string like "1 Jan 12:34\"
    :param dt: the unix timestamp
    :return: the formatted string
    """
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


def read_config() -> Config:
    """
    Reads the configuration file and returns a Config object
    :return: the configuration
    """
    config = Config()

    with open('config.txt') as f:
        for line in f:
            if line.startswith('ssid='):
                config.ssid = line[5:].strip()
            elif line.startswith('password='):
                config.password = line[9:].strip()
            elif line.startswith('lat='):
                config.lat = line[4:].strip()
            elif line.startswith('lon='):
                config.lon = line[4:].strip()
            elif line.startswith('openweathermap_key='):
                config.openweathermap_key = line[19:].strip()
            elif line.startswith('sleep_mins='):
                config.sleep_mins = int(line[11:].strip())

    return config


def sentence_join(inputs: list[str]) -> str:
    """
    Joins the given list of strings into a sentence, using commas and an 'and' as appropriate
    :param inputs: the list of strings
    :return: the sentence
    """
    if len(inputs) == 0:
        return ""
    elif len(inputs) == 1:
        return inputs[0]
    elif len(inputs) == 2:
        return f"{inputs[0]} and {inputs[1]}"
    else:
        return f"{', '.join(inputs[:-1])}, and {inputs[-1]}"


def ensure_suffix(to_check: str, suffix: str) -> str:
    """
    Ensures that the input ends with the given suffix.
    :param to_check: the string to check
    :param suffix: the suffix
    :return: the suffixed string
    """
    if to_check[-1] == suffix:
        return to_check
    else:
        return to_check + suffix
