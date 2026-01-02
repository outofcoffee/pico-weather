from writer import Writer
import fonts.freesans18 as freesans18
import fonts.freesans20 as freesans20
import fonts.freesans24 as freesans24
import framebuf


class FontSize:
    SMALL = 18   # Body text
    MEDIUM = 20  # Headers
    LARGE = 24   # Temperatures


class FrameBufferAdapter(framebuf.FrameBuffer):
    """Adapter that makes DisplayWrapper compatible with Writer's isinstance check."""

    def __init__(self, display_wrapper):
        # Create a minimal 1-byte buffer to satisfy FrameBuffer.__init__
        # We won't actually use this buffer - all operations delegate to display_wrapper
        super().__init__(bytearray(1), 1, 1, framebuf.MONO_HLSB)
        self._display = display_wrapper

    @property
    def width(self):
        return self._display.width

    @property
    def height(self):
        return self._display.height

    def blit(self, fb, x, y):
        self._display.blit(fb, x, y)

    def scroll(self, dx, dy):
        self._display.scroll(dx, dy)

    def fill_rect(self, x, y, w, h, c):
        self._display.fill_rect(x, y, w, h, c)


class FontRenderer:
    """Wrapper around Writer class for DisplayController integration."""

    def __init__(self, display_wrapper):
        # Wrap the display in a FrameBuffer adapter for Writer compatibility
        self._fb = FrameBufferAdapter(display_wrapper)
        self._writers = {
            FontSize.SMALL: Writer(self._fb, freesans18, verbose=False),
            FontSize.MEDIUM: Writer(self._fb, freesans20, verbose=False),
            FontSize.LARGE: Writer(self._fb, freesans24, verbose=False),
        }

    def set_position(self, x: int, y: int):
        """Set text cursor (Writer.set_textpos is static)."""
        Writer.set_textpos(self._fb, y, x)

    def render_text(self, text: str, font_size: int = FontSize.SMALL) -> int:
        """Render text, return height."""
        writer = self._writers.get(font_size, self._writers[FontSize.SMALL])
        writer.printstring(text, invert=True)
        return writer.height

    def get_text_width(self, text: str, font_size: int = FontSize.SMALL) -> int:
        """Calculate pixel width without rendering."""
        writer = self._writers.get(font_size, self._writers[FontSize.SMALL])
        return writer.stringlen(text)

    def get_font_height(self, font_size: int = FontSize.SMALL) -> int:
        """Get font height in pixels."""
        writer = self._writers.get(font_size, self._writers[FontSize.SMALL])
        return writer.height
