from config import Config
from render import render
from screen import Screen
from screen_buffered import BufferedScreen
import machine
import utime
import uasyncio as asyncio

from display import get_epd
from font_renderer import FontSize, get_font_renderer
from net import NetworkManager
from display import DisplayController
from config import read_config
from weather import Weather, load_cached_weather, fetch_weather, \
    cache_weather
from server import start_server

def fetch(config: Config, net: NetworkManager, display: DisplayController) -> tuple[Weather, Weather]:
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

    try:
        current, daily = fetch_weather(net, display, config.lat, config.lon, config.openweathermap_key)
    except Exception as e:
        print(f"error fetching weather: {e}")
        display.display_text(
            DisplayController.RENDER_FLAG_FLUSH,
            FontSize.SMALL,
            "Failed to fetch weather",
            f"Cause: {e}"
        )
        display.deep_sleep()

    if current is None or daily is None:
        print(f"Unable to fetch - sleeping for 5 minutes then resetting the device")
        utime.sleep(300)
        machine.reset()

    cache_weather(current, 'current')
    cache_weather(daily, 'daily')

    return current, daily


async def weather_update_loop(config: Config, net: NetworkManager, display: DisplayController, epd: BufferedScreen):
    """Background coroutine that periodically updates weather display"""
    while True:
        current, daily = fetch(config, net, display)
        render(display, current, daily)

        # flush the display
        epd.set_virtual_mode(False)

        display.deep_sleep()

        print(f'sleeping for {config.refresh_mins} minutes')
        await asyncio.sleep(config.refresh_mins * 60)

        # we need to re-init after deep sleep
        epd.init()

        # buffer writes to the display
        epd.set_virtual_mode(True)


async def main_async(config: Config, display: DisplayController, epd: BufferedScreen, net: NetworkManager):
    """Main async function that starts both weather updates and HTTP server"""

    if config.server:
        # Start the HTTP server (registers task with event loop)
        start_server(net, display)

    # Start the weather update loop as a background task
    asyncio.create_task(weather_update_loop(config, net, display, epd))


def main():
    config = read_config()
    net = NetworkManager(config)

    phy_epd = get_epd(config)
    epd = BufferedScreen(phy_epd, virtual_mode=True)

    font_renderer = get_font_renderer(config, epd)

    display = DisplayController(epd, font_renderer)
    display.init()

    epd.init()

    loop = asyncio.get_event_loop()
    loop.create_task(main_async(config, display, epd, net))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('received keyboard interrupt, disconnecting...')
        net.shut_down()
        machine.reset()


if __name__ == '__main__':
    main()
