from screen import Screen


class PaddedScreen(Screen):
    """
    A proxy wrapper that applies padding to drawing operations.

    This proxy intercepts text(), hline(), and blit() calls and offsets their
    coordinates by the configured padding values before forwarding to the wrapped display.

    This allows padding logic to be applied once in a single place, rather than being
    duplicated in each screen implementation.
    """

    def __init__(self, wrapped_screen: Screen):
        """
        Initializes the padding display proxy.

        :param wrapped_screen: The underlying Screen instance to proxy
        """
        super().__init__()
        self._wrapped = wrapped_screen
        # Default padding preserves existing 2px right margin
        self._padding_top = 0
        self._padding_right = 2  # Preserve legacy 2px margin
        self._padding_bottom = 0
        self._padding_left = 0

    @property
    def width(self) -> int:
        """Returns the physical width of the display."""
        return self._wrapped.width

    @property
    def height(self) -> int:
        """Returns the physical height of the display."""
        return self._wrapped.height

    @property
    def max_draw_width(self) -> int:
        """Returns the maximum drawable width accounting for padding."""
        return self.width - self._padding_left - self._padding_right

    @property
    def draw_start_y(self) -> int:
        """Returns the Y coordinate where drawing should start."""
        return self._padding_top

    @property
    def padding_top(self) -> int:
        """Returns the top padding value."""
        return self._padding_top

    @property
    def padding_right(self) -> int:
        """Returns the right padding value."""
        return self._padding_right

    @property
    def padding_bottom(self) -> int:
        """Returns the bottom padding value."""
        return self._padding_bottom

    @property
    def padding_left(self) -> int:
        """Returns the left padding value."""
        return self._padding_left

    def add_padding(self, top: int, right: int, bottom: int, left: int) -> None:
        """
        Sets the padding for the display. All drawing operations will be offset
        by the padding values.

        :param top: Top padding in pixels
        :param right: Right padding in pixels
        :param bottom: Bottom padding in pixels
        :param left: Left padding in pixels
        """
        self._padding_top = top
        self._padding_right = right
        self._padding_bottom = bottom
        self._padding_left = left

    def init(self) -> None:
        """Initializes the display hardware."""
        self._wrapped.init()

    def Clear(self) -> None:
        """Clears the display buffer."""
        self._wrapped.Clear()

    def display(self) -> None:
        """Flushes the buffer to the display."""
        self._wrapped.display()

    def delay_ms(self, ms: int) -> None:
        """Delays for the specified number of milliseconds."""
        self._wrapped.delay_ms(ms)

    def sleep(self) -> None:
        """Puts the display into sleep mode."""
        self._wrapped.sleep()

    def fill(self, color: int) -> None:
        """Fills the framebuffer with the specified color."""
        self._wrapped.fill(color)

    def text(self, s: str, x: int, y: int, c: int) -> None:
        """Draws text on the framebuffer at the specified position with padding applied."""
        self._wrapped.text(s, x + self._padding_left, y + self._padding_top, c)

    def hline(self, x: int, y: int, w: int, c: int) -> None:
        """Draws a horizontal line on the framebuffer with padding applied."""
        self._wrapped.hline(x + self._padding_left, y + self._padding_top, w, c)

    def blit(self, fb, x: int, y: int) -> None:
        """Blits a framebuffer to the display at the specified position with padding applied."""
        self._wrapped.blit(fb, x + self._padding_left, y + self._padding_top)

    def scroll(self, dx: int, dy: int) -> None:
        """Scrolls the framebuffer."""
        self._wrapped.scroll(dx, dy)

    def fill_rect(self, x: int, y: int, w: int, h: int, c: int) -> None:
        """Fills a rectangle with padding applied."""
        self._wrapped.fill_rect(x + self._padding_left, y + self._padding_top, w, h, c)
