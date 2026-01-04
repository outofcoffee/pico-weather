from screen import Screen


class BufferedScreen(Screen):
    """
    A proxy wrapper for Screen that buffers display operations in virtual mode.

    In virtual mode, this proxy buffers all drawing operations (text, hline, blit, fill),
    as well as calls to display(), Clear(), sleep(), and delay_ms().

    When exiting virtual mode, it replays all buffered operations at once, skipping
    sleep() and delay_ms() calls and consolidating to a single final display() call.

    The proxy is transparent to callers and delegates all padding management to the
    wrapped display, ensuring padding logic is applied consistently.

    This reduces the number of physical display refreshes, minimizing flashing and
    improving performance for e-paper displays.
    """

    def __init__(self, wrapped_screen: Screen, virtual_mode = True):
        """
        Initializes the virtual display proxy.

        :param wrapped_screen: The underlying Screen instance to proxy
        """
        super().__init__()
        self._wrapped = wrapped_screen
        self._virtual_mode = virtual_mode
        self._buffered_ops = []

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
        return self._wrapped.max_draw_width

    @property
    def draw_start_y(self) -> int:
        """Returns the Y coordinate where drawing should start."""
        return self._wrapped.draw_start_y

    def set_virtual_mode(self, enabled: bool) -> None:
        """
        Enables or disables virtual mode.

        When disabling virtual mode, all buffered operations are replayed:
        - sleep() and delay_ms() calls are skipped
        - All other operations are executed in order
        - A final display() call is made at the end if any display() was buffered

        :param enabled: True to enable virtual mode, False to disable
        """
        if self._virtual_mode and not enabled:
            # Exiting virtual mode - replay buffered operations
            self._flush_virtual_operations()

        self._virtual_mode = enabled

        if enabled:
            # Entering virtual mode - clear buffer
            self._buffered_ops = []

    def _flush_virtual_operations(self) -> None:
        """
        Replays all buffered operations, skipping sleep() and delay_ms() calls.
        Consolidates all display() calls to a single final display() call.
        """
        has_display_op = False

        for op in self._buffered_ops:
            op_type = op[0]
            print(f"flushing op: {op_type}: {op}")

            if op_type == 'clear':
                #self._wrapped.Clear()
                print("skipping clear")
            elif op_type == 'fill':
                self._wrapped.fill(op[1])
            elif op_type == 'text':
                _, s, x, y, c = op  # type: ignore
                self._wrapped.text(s, x, y, c)
            elif op_type == 'hline':
                _, x, y, w, c = op  # type: ignore
                self._wrapped.hline(x, y, w, c)
            elif op_type == 'blit':
                _, fb, x, y = op  # type: ignore
                self._wrapped.blit(fb, x, y)
            elif op_type == 'scroll':
                _, dx, dy = op  # type: ignore
                self._wrapped.scroll(dx, dy)
            elif op_type == 'fill_rect':
                _, x, y, w, h, c = op  # type: ignore
                self._wrapped.fill_rect(x, y, w, h, c)
            elif op_type == 'display':
                # Mark that we need to display, but don't call it yet
                has_display_op = True
            # Skip 'sleep' and 'delay' - we don't replay these operations

        # Call display() once at the end if any display operations were buffered
        if has_display_op:
            self._wrapped.display()

        # Clear the buffer
        self._buffered_ops = []

    def init(self) -> None:
        """Initializes the display hardware."""
        self._wrapped.init()

    def Clear(self) -> None:
        """
        Clears the display buffer.

        In virtual mode, this discards all previously buffered operations
        and buffers a Clear operation.
        """
        if self._virtual_mode:
            # Clear all previous buffered operations
            self._buffered_ops = [('clear',)]
        else:
            self._wrapped.Clear()

    def display(self) -> None:
        """
        Flushes the buffer to the display.

        In virtual mode, this operation is buffered instead of executed immediately.
        """
        if self._virtual_mode:
            self._buffered_ops.append(('display',))
        else:
            self._wrapped.display()

    def delay_ms(self, ms: int) -> None:
        """
        Delays for the specified number of milliseconds.

        In virtual mode, this operation is buffered but will be skipped
        when operations are replayed (to avoid delays between operations).
        """
        if self._virtual_mode:
            self._buffered_ops.append(('delay', ms))
        else:
            self._wrapped.delay_ms(ms)

    def sleep(self) -> None:
        """
        Puts the display into sleep mode.

        In virtual mode, this operation is buffered but will be skipped
        when operations are replayed (to avoid sleeps between operations).
        """
        if self._virtual_mode:
            self._buffered_ops.append(('sleep',))
        else:
            self._wrapped.sleep()

    def fill(self, color: int) -> None:
        """
        Fills the framebuffer with the specified color.

        In virtual mode, this operation is buffered.
        """
        if self._virtual_mode:
            self._buffered_ops.append(('fill', color))
        else:
            self._wrapped.fill(color)

    def text(self, s: str, x: int, y: int, c: int) -> None:
        """
        Draws text on the framebuffer at the specified position.

        In virtual mode, this operation is buffered.
        """
        if self._virtual_mode:
            self._buffered_ops.append(('text', s, x, y, c))
        else:
            self._wrapped.text(s, x, y, c)

    def hline(self, x: int, y: int, w: int, c: int) -> None:
        """
        Draws a horizontal line on the framebuffer.

        In virtual mode, this operation is buffered.
        """
        if self._virtual_mode:
            self._buffered_ops.append(('hline', x, y, w, c))
        else:
            self._wrapped.hline(x, y, w, c)

    def blit(self, fb, x: int, y: int) -> None:
        """
        Blits a framebuffer to the display at the specified position.

        In virtual mode, this operation is buffered.
        """
        if self._virtual_mode:
            self._buffered_ops.append(('blit', fb, x, y))
        else:
            self._wrapped.blit(fb, x, y)

    def scroll(self, dx: int, dy: int) -> None:
        """Scrolls the framebuffer (virtual mode compatible)."""
        if self._virtual_mode:
            self._buffered_ops.append(('scroll', dx, dy))
        else:
            self._wrapped.scroll(dx, dy)

    def fill_rect(self, x: int, y: int, w: int, h: int, c: int) -> None:
        """Fills a rectangle (virtual mode compatible)."""
        if self._virtual_mode:
            self._buffered_ops.append(('fill_rect', x, y, w, h, c))
        else:
            self._wrapped.fill_rect(x, y, w, h, c)
