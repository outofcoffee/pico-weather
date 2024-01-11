import urequests as requests

import json
import os
import utime

from render import DisplayController
from utils import wrap_text, sentence_join, ensure_suffix, dir_exists, file_exists


class Temperature:
    main: float
    temp_min: float
    temp_max: float

    def __init__(self, main: float, temp_min: float, temp_max: float):
        self.main = main
        self.temp_min = temp_min
        self.temp_max = temp_max


class Weather:
    dt: int
    temp: Temperature
    titles: list[str]
    description: str
    day_summary: list[str]

    def __init__(self, dt: int, temp: Temperature, titles: list[str], description: str, day_summary: list[str]):
        self.dt = dt
        self.temp = temp
        self.titles = titles
        self.description = description
        self.day_summary = day_summary

    def to_dict(self):
        return {
            'dt': self.dt,
            'temp': {
                'main': self.temp.main,
                'temp_min': self.temp.temp_min,
                'temp_max': self.temp.temp_max,
            },
            'titles': self.titles,
            'description': self.description,
            'day_summary': self.day_summary,
        }

    @classmethod
    def from_dict(cls, data):
        temp = Temperature(data['temp']['main'], data['temp']['temp_min'], data['temp']['temp_max'])
        return cls(data['dt'], temp, data['titles'], data['description'], data['day_summary'])


CACHE_DIR = 'cache'


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

    daily_conditions = resp['daily']

    # multiple daily forecasts; first element is today
    if len(daily_conditions) > 0:
        today_conditions = daily_conditions[0]
        (daily_temp, daily_titles, daily_desc) = summarise_conditions('daily', today_conditions)

        today_summary = ensure_suffix(today_conditions['summary'], ".")
        day_summary = wrap_text(today_summary, DisplayController.MAX_TEXT_WIDTH)
        daily = Weather(dt, daily_temp, daily_titles, daily_desc, day_summary)

    else:
        print(f"no daily weather returned")
        daily = Weather(dt, Temperature(0, 0, 0), [], "", [])

    return current, daily


def summarise_conditions(weather_timeframe, conditions) -> tuple[Temperature, list[str], str]:
    """
    Summarises the given current conditions and returns a tuple of (temp, titles, description)
    :param weather_timeframe: the weather timeframe, e.g. 'current' or 'daily'
    :param conditions: the conditions
    :return: a tuple of (temp, titles, description)
    """
    temp: Temperature
    if isinstance(conditions['temp'], dict):
        temp = Temperature(
            kelvin_to_celsius(conditions['temp']['day']),
            kelvin_to_celsius(conditions['temp']['min']),
            kelvin_to_celsius(conditions['temp']['max']),
        )
    else:
        single_temp = kelvin_to_celsius(conditions['temp'])
        temp = Temperature(single_temp, single_temp, single_temp)

    weathers = conditions['weather']
    print(f"{len(weathers)} {weather_timeframe} weather(s): ", weathers)

    summary: tuple[Temperature, list[str], str]
    if len(weathers) > 0:
        titles: list[str] = []
        descriptions: list[str] = []

        for weather in weathers:
            titles.append(weather['main'])
            descriptions.append(weather['description'])

        summary = temp, titles, sentence_join(descriptions)

    else:
        print(f"no {weather_timeframe} weather returned")
        summary = temp, [], ""

    print(f"{weather_timeframe}: {summary}")
    return summary


def kelvin_to_celsius(temp: float) -> float:
    """
    Converts the given temperature from Kelvin to Celsius
    :param temp: the temperature in Kelvin
    :return: the temperature in Celsius
    """
    return temp - 273.15


def ensure_cache_dir():
    """
    Ensures that the cache directory exists.
    """
    if not dir_exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)


def is_cache_valid(timeframe: str, cache_mins: int) -> bool:
    """
    Returns the timestamp of the most recent cached weather data, or 0 if no cache exists.
    :param timeframe: the timeframe
    :param cache_mins: the cache expiry in minutes
    """
    ensure_cache_dir()

    is_valid: bool
    if file_exists(f'{CACHE_DIR}/{timeframe}_timestamp'):
        with open(f'{CACHE_DIR}/{timeframe}_timestamp', 'r') as f:
            timestamp = int(f.read())
            age = utime.time() - timestamp
            print(f"cache for {timeframe} is {age} seconds old")

            # if age is negative, the device RTC is probably not set
            is_valid = 0 <= age < (cache_mins * 60)

    else:
        is_valid = False

    print(f"cache for {timeframe} is {'valid' if is_valid else 'invalid'} (expiry {cache_mins} mins)")
    return is_valid


def cache_weather(weather: Weather, timeframe: str):
    """
    Caches the given weather.
    :param weather: the weather
    :param timeframe: the timeframe
    """
    ensure_cache_dir()
    print(f"caching weather for {timeframe}")

    with open(f'{CACHE_DIR}/{timeframe}.json', 'w') as f:
        weather_json = json.dumps(weather.to_dict())
        f.write(weather_json)

    with open(f'{CACHE_DIR}/{timeframe}_timestamp', 'w') as f:
        # write the current timestamp
        # note, this is not necessarily the same as the weather.dt timestamp
        # is it depends on the device RTC
        f.write(str(utime.time()))


def load_cached_weather(timeframe: str, cache_mins: int) -> Weather:
    """
    Returns the cached weather, or None if no cache exists.
    :param timeframe: the timeframe
    :param cache_mins: the cache expiry in minutes
    """
    if not is_cache_valid(timeframe, cache_mins):
        return None

    ensure_cache_dir()
    if file_exists(f'{CACHE_DIR}/{timeframe}.json'):
        with open(f'{CACHE_DIR}/{timeframe}.json', 'r') as f:
            weather_json = f.read()
            print(f"loaded cached weather for {timeframe}", weather_json)
            weather_dict = json.loads(weather_json)
            return Weather.from_dict(weather_dict)
    else:
        print(f"cache for {timeframe} does not exist")
        return None
