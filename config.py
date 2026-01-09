class Config:
    ssid: str
    password: str
    lat: str | None
    lon: str | None
    zip: str | None
    country: str | None
    openweathermap_key: str
    refresh_mins: int
    cache_mins: int
    display_size: str
    padding: tuple[int, int, int, int] | None
    text_renderer: str


def read_config() -> Config:
    """
    Reads the configuration file and returns a Config object
    :return: the configuration
    """
    config = Config()
    config.lat = None
    config.lon = None
    config.zip = None
    config.country = None
    config.padding = None
    config.text_renderer = 'basic'

    # Supported configuration keys
    supported_keys = [
        'ssid',
        'password',
        'lat',
        'lon',
        'zip',
        'country',
        'openweathermap_key',
        'refresh_mins',
        'cache_mins',
        'display_size',
        'padding',
        'text_renderer'
    ]

    with open('config.txt') as f:
        for line in f:
            if line.startswith('#'):
                # ignore comments
                continue

            # Check each supported key
            for key in supported_keys:
                key_prefix = key + '='
                if line.startswith(key_prefix):
                    # Calculate offset: key length + equals sign
                    offset = len(key) + 1
                    value = line[offset:].strip()

                    # Handle special cases for type conversion and parsing
                    if key == 'refresh_mins' or key == 'cache_mins':
                        setattr(config, key, int(value))
                    elif key == 'padding':
                        parts = value.split(',')
                        if len(parts) == 4:
                            config.padding = (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
                    else:
                        setattr(config, key, value)
                    break

    return config