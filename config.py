class Config:
    ssid: str
    password: str
    lat: str
    lon: str
    openweathermap_key: str
    refresh_mins: int
    cache_mins: int
    display_size: str
    padding: tuple[int, int, int, int] | None
    text_renderer: str
    server: bool
    listen_port: int


def read_config() -> Config:
    """
    Reads the configuration file and returns a Config object
    :return: the configuration
    """
    config = Config()
    config.padding = None
    config.text_renderer = 'basic'
    config.server = False
    config.listen_port = 80

    with open('config.txt') as f:
        for line in f:
            if line.startswith('#'):
                # ignore comments
                continue
            elif line.startswith('ssid='):
                config.ssid = line[5:].strip()
            elif line.startswith('password='):
                config.password = line[9:].strip()
            elif line.startswith('lat='):
                config.lat = line[4:].strip()
            elif line.startswith('lon='):
                config.lon = line[4:].strip()
            elif line.startswith('openweathermap_key='):
                config.openweathermap_key = line[19:].strip()
            elif line.startswith('refresh_mins='):
                config.refresh_mins = int(line[13:].strip())
            elif line.startswith('cache_mins='):
                config.cache_mins = int(line[11:].strip())
            elif line.startswith('display_size='):
                config.display_size = line[13:].strip()
            elif line.startswith('padding='):
                padding_str = line[8:].strip()
                parts = padding_str.split(',')
                if len(parts) == 4:
                    config.padding = (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
            elif line.startswith('text_renderer='):
                config.text_renderer = line[14:].strip()
            elif line.startswith('server='):
                config.server = bool(line[7:].strip())
            elif line.startswith('listen_port='):
                config.listen_port = int(line[12:].strip())

    return config
