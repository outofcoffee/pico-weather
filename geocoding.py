import urequests as requests
import json
import os
import utime

from utils import dir_exists, file_exists


CACHE_DIR = 'cache'


class GeocodingResult:
    """Represents a geocoding lookup result"""
    zip: str
    country: str
    name: str
    lat: str
    lon: str

    def __init__(self, zip_code: str, country: str, name: str, lat: str, lon: str):
        self.zip = zip_code
        self.country = country
        self.name = name
        self.lat = lat
        self.lon = lon

    def to_dict(self):
        return {
            'zip': self.zip,
            'country': self.country,
            'name': self.name,
            'lat': self.lat,
            'lon': self.lon,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['zip'], data['country'], data['name'], data['lat'], data['lon'])


def get_cache_key(zip_code: str, country: str) -> str:
    """
    Returns a cache key for the given zip/postcode and country
    :param zip_code: the zip/postcode
    :param country: the country code
    :return: the cache key
    """
    return f"{zip_code}_{country}"


def ensure_cache_dir():
    """
    Ensures that the cache directory exists.
    """
    if not dir_exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)


def is_geocoding_cache_valid(zip_code: str, country: str, cache_mins: int) -> bool:
    """
    Checks if the cached geocoding result is still valid
    :param zip_code: the zip/postcode
    :param country: the country code
    :param cache_mins: the cache expiry in minutes
    :return: True if cache is valid, False otherwise
    """
    ensure_cache_dir()
    cache_key = get_cache_key(zip_code, country)

    is_valid: bool
    timestamp_file = f'{CACHE_DIR}/geocoding_{cache_key}_timestamp'
    if file_exists(timestamp_file):
        with open(timestamp_file, 'r') as f:
            timestamp = int(f.read())
            age = utime.time() - timestamp
            print(f"geocoding cache for {cache_key} is {age} seconds old")

            # if age is negative, the device RTC is probably not set
            is_valid = 0 <= age < (cache_mins * 60)

    else:
        is_valid = False

    print(f"geocoding cache for {cache_key} is {'valid' if is_valid else 'invalid'} (expiry {cache_mins} mins)")
    return is_valid


def cache_geocoding(result: GeocodingResult, cache_mins: int):
    """
    Caches the geocoding result
    :param result: the geocoding result
    :param cache_mins: the cache expiry in minutes (used for logging only)
    """
    ensure_cache_dir()
    cache_key = get_cache_key(result.zip, result.country)
    print(f"caching geocoding result for {cache_key} (expiry {cache_mins} mins)")

    with open(f'{CACHE_DIR}/geocoding_{cache_key}.json', 'w') as f:
        result_json = json.dumps(result.to_dict())
        f.write(result_json)

    with open(f'{CACHE_DIR}/geocoding_{cache_key}_timestamp', 'w') as f:
        f.write(str(utime.time()))


def load_cached_geocoding(zip_code: str, country: str, cache_mins: int) -> GeocodingResult | None:
    """
    Loads the cached geocoding result if it exists and is valid
    :param zip_code: the zip/postcode
    :param country: the country code
    :param cache_mins: the cache expiry in minutes
    :return: the cached geocoding result, or None if not found or invalid
    """
    if not is_geocoding_cache_valid(zip_code, country, cache_mins):
        return None

    ensure_cache_dir()
    cache_key = get_cache_key(zip_code, country)
    cache_file = f'{CACHE_DIR}/geocoding_{cache_key}.json'

    if file_exists(cache_file):
        with open(cache_file, 'r') as f:
            result_json = f.read()
            print(f"loaded cached geocoding for {cache_key}: {result_json}")
            result_dict = json.loads(result_json)
            return GeocodingResult.from_dict(result_dict)
    else:
        print(f"geocoding cache for {cache_key} does not exist")
        return None


def fetch_geocoding(zip_code: str, country: str, openweathermap_key: str) -> GeocodingResult:
    """
    Fetches geocoding data from OpenWeatherMap API (no caching)
    :param zip_code: the zip/postcode
    :param country: the country code (e.g. 'GB', 'US')
    :param openweathermap_key: the OpenWeatherMap API key
    :return: the geocoding result
    """
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zip_code},{country}&appid={openweathermap_key}"
    print(f"geocoding API lookup: {url}")
    r = requests.get(url)
    resp: dict = r.json()
    r.close()

    lat = str(resp['lat'])
    lon = str(resp['lon'])
    name = resp['name']

    print(f"geocoding result: {name} ({resp['country']}) -> lat={lat}, lon={lon}")

    return GeocodingResult(zip_code, country, name, lat, lon)


def lookup_geocoding(zip_code: str, country: str, openweathermap_key: str, cache_mins: int) -> tuple[str, str]:
    """
    Looks up the latitude and longitude for a given zip/postcode and country code.
    First checks the cache, then calls the API if needed.
    :param zip_code: the zip/postcode
    :param country: the country code (e.g. 'GB', 'US')
    :param openweathermap_key: the OpenWeatherMap API key
    :param cache_mins: the cache expiry in minutes
    :return: tuple of (lat, lon) as strings
    """
    # Try to load from cache first
    cached = load_cached_geocoding(zip_code, country, cache_mins)
    if cached is not None:
        print(f"using cached geocoding: {cached.name} -> lat={cached.lat}, lon={cached.lon}")
        return cached.lat, cached.lon

    # Cache miss - fetch from API
    print(f"no cached geocoding found; fetching from API")
    result = fetch_geocoding(zip_code, country, openweathermap_key)

    # Cache the result
    cache_geocoding(result, cache_mins)

    return result.lat, result.lon
