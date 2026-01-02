from utils import Config
from display_wrapper import DisplayWrapper, EPD_7in5_B_Wrapper, EPD_2in13_V3_Wrapper
from display_padding import PaddingDisplayProxy


def get_epd(config: Config) -> DisplayWrapper:
    """
    Factory function that returns the appropriate EPD wrapper based on config.
    Adapts different manufacturer EPD implementations to a common DisplayWrapper interface.
    Wraps the display with PaddingDisplayProxy to apply padding if configured.
    """
    wrapper: DisplayWrapper
    if config.display_size == 'large':
        wrapper = EPD_7in5_B_Wrapper()
    elif config.display_size == 'small':
        wrapper = EPD_2in13_V3_Wrapper()
    else:
        raise ValueError(f"Unsupported display_size: {config.display_size}. Must be 'large' or 'small'.")

    if config.padding is not None:
        wrapper = PaddingDisplayProxy(wrapper)
        wrapper.add_padding(config.padding[0], config.padding[1], config.padding[2], config.padding[3])

    return wrapper
