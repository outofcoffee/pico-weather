import urequests as requests

from render import MAX_TEXT_WIDTH
from utils import wrap_text, sentence_join, ensure_suffix


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


def get_img_for_title(title: str) -> str:
    """
    Returns the image path for the given weather title
    :param title: the weather title
    :return: the image path
    """
    # convert title to image per https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
    if title == 'Clouds':
        img_path = 'cloud'
    elif title == 'Mist' or title == 'Smoke' or title == 'Haze' or title == 'Dust' or title == 'Fog' or title == 'Sand' or title == 'Dust' or title == 'Ash' or title == 'Squall' or title == 'Tornado':
        img_path = 'fog'
    elif title == 'Rain' or title == 'Drizzle':
        img_path = 'rain'
    elif title == 'Thunderstorm':
        img_path = 'lightning'
    elif title == 'Snow':
        img_path = 'snow'
    elif title == 'Clear':
        img_path = 'sun'
    else:
        print(f"unknown weather.title: {title}")
        img_path = None

    return img_path


def fetch_weather(lat: str, lon: str, openweathermap_key: str) -> tuple[Weather, Weather]:
    """
    Fetches the current weather from OpenWeatherMap and returns a tuple
    of Weather objects [current, daily]
    :param lat: the latitude
    :param lon: the longitude
    :param openweathermap_key: the OpenWeatherMap API key
    :return: the Weather objects
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

    (current_temp, current_titles, current_desc) = summarise_conditions('current', current_conditions)
    current = Weather(dt, current_temp, current_titles, current_desc, [])

    # multiple daily forecasts
    daily_conditions = resp['daily']
    if len(daily_conditions) > 0:
        today_conditions = daily_conditions[0]
        (daily_temp, daily_titles, daily_desc) = summarise_conditions('daily', today_conditions)

        today_summary = ensure_suffix(today_conditions['summary'], ".")
        day_summary = wrap_text(today_summary, MAX_TEXT_WIDTH)
        daily = Weather(dt, daily_temp, daily_titles, daily_desc, day_summary)

    else:
        print(f"no daily weather returned")
        daily = Weather(dt, 0, [], "", [])

    return current, daily


def summarise_conditions(weather_timeframe, conditions) -> tuple[float, list[str], str]:
    """
    Summarises the given current conditions and returns a tuple of (temp, titles, description)
    :param weather_timeframe: the weather timeframe, e.g. 'current' or 'daily'
    :param conditions: the conditions
    :return: a tuple of (temp, titles, description)
    """
    temp: float
    if isinstance(conditions['temp'], dict):
        temp = conditions['temp']['day']
    else:
        temp = conditions['temp']

    # convert from K to C
    temp_in_celsius: float = temp - 273.15

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
