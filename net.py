from config import Config
from display import DisplayController
from font_renderer import FontSize
import network
import utime


def _connect_to_network(ssid: str, password: str) -> tuple[network.WLAN, str]:
    """
    Connects to the configured network and returns the WLAN client and IP address.
    """
    print(f"connecting to {ssid}...")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('waiting for connection...')
        utime.sleep(1)

    ifconfig = wlan.ifconfig()
    print(ifconfig)

    ip_addr = ifconfig[0]
    print(f'connected on {ip_addr}')
    return wlan, ip_addr


def _disconnect(wlan: network.WLAN):
    """
    Disconnects from the given WLAN client.
    """
    print('disconnecting from network')
    wlan.disconnect()
    wlan.active(False)


class NetworkManager:
    count: int
    net: tuple[network.WLAN, str] | None

    def __init__(self, config: Config) -> None:
        self.config = config
        self.count = 0
        self.net = None

    def use_net(self) -> None:
        if self.count == 0:
            self.net = _connect_to_network(self.config.ssid, self.config.password)

        self.count += 1

    def return_net(self) -> None:
        if self.net == None or self.count < 1:
            print(f"warning - no active network to return")
            return
        
        self.count -= 1
        if self.count == 0:
            _disconnect(self.net[0]) # type: ignore
            self.net = None

    @property
    def active(self) -> bool:
        return self.count > 0

    @property
    def ip(self) -> str:
        if not self.active or self.net == None:
            raise AssertionError("No active network connection")
        
        return self.net[0].ifconfig()[0]
    
    def shut_down(self) -> None:
        for _ in range(self.count):
            self.return_net()


def connect_to_network(net: NetworkManager, display: DisplayController) -> str:
    """
    Convenience function that connects to the network
    and updates the display with progress.
    
    :param net: network manager
    :param display: display controller
    :return: IP address
    :rtype: str
    """
    display.display_text(
            DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_FLUSH,
            FontSize.SMALL,
            f"Connecting to {net.config.ssid}..."
        )
    net.use_net()
    ip = net.ip

    display.display_text(
            DisplayController.RENDER_FLAG_FLUSH,
            FontSize.SMALL,
            "Connected",
            f"IP: {ip}"
        )

    return ip
