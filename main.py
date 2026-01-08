from config import Config
from render import render
from screen_buffered import BufferedScreen
import machine
import utime

from display import get_epd
from font_renderer import FontSize, get_font_renderer
from net import connect_to_network, disconnect
from display import DisplayController
from config import read_config
from weather import Weather, load_cached_weather, fetch_weather, \
    cache_weather
from geocoding import lookup_geocoding


def fetch(config: Config, display: DisplayController) -> tuple[Weather, Weather]:
    """
    First tries to load the weather from the cache. If it's not there, connects to the configured network, fetches the
    weather, disconnects, and caches the weather.
    :param config: the configuration
    :param display: the display controller
    :return: the current and daily weather
    """
    current: Weather | None = load_cached_weather('current', config.cache_mins)
    daily: Weather | None = load_cached_weather('daily', config.cache_mins)

    if current is not None and daily is not None:
        print(f"using cached weather")
        return current, daily
    else:
        print(f"no cached weather found; fetching from remote")

    display.display_text(
        DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_FLUSH,
        FontSize.SMALL,
        f"Connecting to {config.ssid}..."
    )

    try:
        wlan, ip = connect_to_network(config.ssid, config.password)
    except KeyboardInterrupt:
        print('received keyboard interrupt when connecting to network')
        machine.reset()

    display.display_text(
        DisplayController.RENDER_FLAG_FLUSH,
        FontSize.SMALL,
        "Connected",
        f"IP: {ip}"
    )

    # Determine lat/lon - either from config or via geocoding lookup
    lat = config.lat
    lon = config.lon

    if lat is None or lon is None:
        if config.zip is not None and config.country is not None:
            print(f"performing geocoding lookup for {config.zip}, {config.country}")
            display.display_text(
                DisplayController.RENDER_FLAG_FLUSH,
                FontSize.SMALL,
                f"Looking up location..."
            )
            try:
                lat, lon = lookup_geocoding(config.zip, config.country, config.openweathermap_key)
            except Exception as e:
                print(f"error during geocoding lookup: {e}")
                display.display_text(
                    DisplayController.RENDER_FLAG_FLUSH,
                    FontSize.SMALL,
                    "Failed to lookup location",
                    f"Cause: {e}"
                )
                display.deep_sleep()
                disconnect(wlan)
                utime.sleep(300)
                machine.reset()
        else:
            print(f"error: must specify either lat/lon or zip/country in config.txt")
            display.display_text(
                DisplayController.RENDER_FLAG_FLUSH,
                FontSize.SMALL,
                "Config error:",
                "Must specify lat/lon",
                "or zip/country"
            )
            display.deep_sleep()
            disconnect(wlan)
            utime.sleep(300)
            machine.reset()

    try:
        current, daily = fetch_weather(display, lat, lon, config.openweathermap_key)
    except Exception as e:
        print(f"error fetching weather: {e}")
        display.display_text(
            DisplayController.RENDER_FLAG_FLUSH,
            FontSize.SMALL,
            "Failed to fetch weather",
            f"Cause: {e}"
        )
        display.deep_sleep()
    finally:
        # we don't need the network anymore
        disconnect(wlan)

    if current is None or daily is None:
        print(f"Unable to fetch - sleeping for 5 minutes then resetting the device")
        utime.sleep(300)
        machine.reset()

    cache_weather(current, 'current')
    cache_weather(daily, 'daily')

    return current, daily


def main():
    config = read_config()
 
    phy_epd = get_epd(config)
    epd = BufferedScreen(phy_epd, virtual_mode=False)

    font_renderer = get_font_renderer(config, epd)

    display = DisplayController(epd, font_renderer)
    display.init()

    while True:
        # we need to re-init after deep sleep
        epd.init()

        # buffer writes to the display
        epd.set_virtual_mode(True)

        current, daily = fetch(config, display)
        render(display, current, daily)

        # flush the display
        epd.set_virtual_mode(False)

        display.deep_sleep()

        print(f'sleeping for {config.refresh_mins} minutes')
        utime.sleep(config.refresh_mins * 60)


if __name__ == '__main__':
    main()
