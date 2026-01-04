from writer import Writer
import fonts.freesans18 as freesans18
import fonts.freesans20 as freesans20
import fonts.freesans24 as freesans24
import framebuf


class FontSize:
    SMALL = 18   # Body text
    MEDIUM = 20  # Headers
    LARGE = 24   # Temperatures


class FontRenderer:
    """Abstract base class for text rendering."""

    def render_text(self, text: str, font_size: int) -> int:
        """Render text at current cursor position. Returns height of rendered text."""
        raise NotImplementedError

    def get_text_width(self, text: str, font_size: int) -> int:
        """Calculate pixel width of text without rendering."""
        raise NotImplementedError

    def get_font_height(self, font_size: int) -> int:
        """Get font height in pixels."""
        raise NotImplementedError

    def set_position(self, x: int, y: int):
        """Set text cursor position."""
        raise NotImplementedError

    def get_current_position(self) -> tuple:
        """Get current cursor position as (x, y)."""
        raise NotImplementedError


class BasicTextRenderer(FontRenderer):
    """Basic text renderer using Screen's built-in text() method."""

    # Fixed 8-pixel character width for built-in font
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8

    def __init__(self, screen):
        self._screen = screen
        self._cursor_x = 0
        self._cursor_y = 0

    def render_text(self, text: str, font_size: int = FontSize.SMALL) -> int:
        """Render text using epd.text(). font_size is ignored."""
        self._screen.text(text, self._cursor_x, self._cursor_y, 0x00)
        return self.CHAR_HEIGHT

    def get_text_width(self, text: str, font_size: int = FontSize.SMALL) -> int:
        """Calculate pixel width. font_size is ignored."""
        return len(text) * self.CHAR_WIDTH

    def get_font_height(self, font_size: int = FontSize.SMALL) -> int:
        """Returns fixed height. font_size is ignored."""
        return self.CHAR_HEIGHT

    def set_position(self, x: int, y: int):
        """Set text cursor position."""
        self._cursor_x = x
        self._cursor_y = y

    def get_current_position(self) -> tuple:
        """Get current cursor position as (x, y)."""
        return (self._cursor_x, self._cursor_y)


class FrameBufferAdapter(framebuf.FrameBuffer):
    """Adapter that makes Screen compatible with Writer's isinstance check."""

    def __init__(self, screen):
        # Create a minimal 1-byte buffer to satisfy FrameBuffer.__init__
        # We won't actually use this buffer - all operations delegate to screen
        super().__init__(bytearray(1), 1, 1, framebuf.MONO_HLSB)
        self._screen = screen

    @property
    def width(self):
        return self._screen.width

    @property
    def height(self):
        return self._screen.height

    def blit(self, fb, x, y):
        self._screen.blit(fb, x, y)

    def scroll(self, dx, dy):
        self._screen.scroll(dx, dy)

    def fill_rect(self, x, y, w, h, c):
        self._screen.fill_rect(x, y, w, h, c)


class RichTextRenderer(FontRenderer):
    """Rich text renderer using Writer class with bitmap fonts."""

    def __init__(self, screen):
        # Wrap the display in a FrameBuffer adapter for Writer compatibility
        self._fb = FrameBufferAdapter(screen)
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

    def get_current_position(self) -> tuple:
        """Get current cursor position (col, row) from Writer state."""
        state = Writer.state.get(id(self._fb))
        if state:
            return (state.text_col, state.text_row)
        return (0, 0)
