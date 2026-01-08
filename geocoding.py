import urequests as requests
import json
import os

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


def is_geocoding_cache_valid(zip_code: str, country: str) -> bool:
    """
    Checks if the cached geocoding result exists
    :param zip_code: the zip/postcode
    :param country: the country code
    :return: True if cache exists, False otherwise
    """
    ensure_cache_dir()
    cache_key = get_cache_key(zip_code, country)
    cache_file = f'{CACHE_DIR}/geocoding_{cache_key}.json'

    is_valid = file_exists(cache_file)
    print(f"geocoding cache for {cache_key} {'exists' if is_valid else 'does not exist'}")
    return is_valid


def cache_geocoding(result: GeocodingResult):
    """
    Caches the geocoding result permanently (no expiry)
    :param result: the geocoding result
    """
    ensure_cache_dir()
    cache_key = get_cache_key(result.zip, result.country)
    print(f"caching geocoding result for {cache_key}")

    with open(f'{CACHE_DIR}/geocoding_{cache_key}.json', 'w') as f:
        result_json = json.dumps(result.to_dict())
        f.write(result_json)


def load_cached_geocoding(zip_code: str, country: str) -> GeocodingResult | None:
    """
    Loads the cached geocoding result if it exists
    :param zip_code: the zip/postcode
    :param country: the country code
    :return: the cached geocoding result, or None if not found
    """
    if not is_geocoding_cache_valid(zip_code, country):
        return None

    cache_key = get_cache_key(zip_code, country)
    cache_file = f'{CACHE_DIR}/geocoding_{cache_key}.json'

    with open(cache_file, 'r') as f:
        result_json = f.read()
        print(f"loaded cached geocoding for {cache_key}: {result_json}")
        result_dict = json.loads(result_json)
        return GeocodingResult.from_dict(result_dict)


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


def lookup_geocoding(zip_code: str, country: str, openweathermap_key: str) -> tuple[str, str]:
    """
    Looks up the latitude and longitude for a given zip/postcode and country code.
    First checks the cache, then calls the API if needed. Results are cached permanently.
    :param zip_code: the zip/postcode
    :param country: the country code (e.g. 'GB', 'US')
    :param openweathermap_key: the OpenWeatherMap API key
    :return: tuple of (lat, lon) as strings
    """
    # Try to load from cache first
    cached = load_cached_geocoding(zip_code, country)
    if cached is not None:
        print(f"using cached geocoding: {cached.name} -> lat={cached.lat}, lon={cached.lon}")
        return cached.lat, cached.lon

    # Cache miss - fetch from API
    print(f"no cached geocoding found; fetching from API")
    result = fetch_geocoding(zip_code, country, openweathermap_key)

    # Cache the result permanently
    cache_geocoding(result)

    return result.lat, result.lon
