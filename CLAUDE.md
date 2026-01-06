# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a MicroPython project for Raspberry Pi Pico W that fetches weather data from OpenWeather API and displays it on a Waveshare e-paper display. The code runs directly on the Pico W microcontroller.

## Development Commands

### Deploying to Pico W

Upload all Python files and config to the connected Pico W device:
```bash
./scripts/upload.sh
```

Upload specific files:
```bash
./scripts/upload.sh config.txt display.py weather.py
```

Or using the Python script directly:
```bash
python3 ./scripts/microupload.py -v /dev/cu.usbmodem14101 config.txt display.py main.py
```

### Deleting Files from Pico W

Remove all files from the device:
```bash
./scripts/delete.sh
```

### Running a REPL Session

Activate virtual environment and connect to Pico W:
```bash
source venv/bin/activate
pip install mpremote  # if not already installed
mpremote
```

Exit REPL with `Ctrl-]`

### Setup

1. Copy `config.txt.example` to `config.txt` and fill in:
   - WiFi credentials
   - Location (either lat/lon coordinates OR zip/postcode and country code)
   - OpenWeather API key
2. Ensure MicroPython is installed on the Pico W (firmware files included in repo: `RPI_PICO2_W-20251209-v1.27.0.uf2` and `RPI_PICO_W-20231227-v1.22.0.uf2`)

## Architecture

### MicroPython Constraints

**Critical**: This code runs on MicroPython, NOT standard Python. Key differences:
- Limited standard library (use `u*` variants: `urequests`, `utime`, `ujson` where applicable)
- No `match` statement support (use `if/elif` chains instead)
- Memory constraints - keep data structures minimal
- No type hints at runtime (they're used for documentation only)
- File I/O uses basic `os` module functions

### Core Components

The architecture uses a layered approach separating hardware abstraction (**Screen**) from high-level rendering control (**DisplayController**).

**[main.py](main.py)** - Entry point and orchestration
- `main()` runs the infinite loop: init display → fetch weather → render → sleep → repeat
- `fetch()` handles caching logic and network connection lifecycle
- Creates a `BufferedScreen` wrapping the physical screen for operation buffering

**[config.py](config.py)** - Configuration management
- `Config` class holds configuration data (WiFi, location, API keys, display settings)
- `read_config()` parses `config.txt` key=value format
- Supports `text_renderer` field to choose between basic and rich text rendering

**[screen.py](screen.py)** - Hardware abstraction layer
- `Screen` base class defines the interface for e-paper hardware operations
- `EPD_7in5_B_Wrapper` wraps large 7.5" display, normalizing its interface
- `EPD_2in13_V3_Wrapper` wraps small 2.13" display, normalizing its interface
- Properties: `width`, `height`, `max_draw_width`, `draw_start_y`

**[screen_padded.py](screen_padded.py)** - Padding decorator
- `PaddedScreen` intercepts drawing operations and applies padding offsets
- Transforms coordinates for `text()`, `hline()`, `blit()` operations
- Default 2px right margin preserved for legacy compatibility
- Exposes `max_draw_width` and `draw_start_y` accounting for padding

**[screen_buffered.py](screen_buffered.py)** - Buffering decorator
- `BufferedScreen` buffers all drawing operations in virtual mode
- When virtual mode disabled, replays buffered operations
- Skips `sleep()` and `delay_ms()` calls during replay
- Consolidates multiple `display()` calls into single refresh

**[display.py](display.py)** - Display controller and factory
- `DisplayController` provides high-level rendering API
- Manages text rendering via `FontRenderer`, tracks vertical cursor position
- Uses bitwise render flags (`RENDER_FLAG_CLEAR`, `RENDER_FLAG_APPEND_ONLY`, `RENDER_FLAG_FLUSH`, etc.)
- Methods: `display_text(flags, font_size, *lines)`, `display_right(flags, font_size, text)`
- `get_epd()` factory function creates appropriate `Screen` based on config

**[font_renderer.py](font_renderer.py)** - Font rendering abstraction
- `FontRenderer` abstract base class for text rendering
- `BasicTextRenderer` uses MicroPython's built-in 8x8 monospace font
- `RichTextRenderer` uses Writer library with TrueType fonts (18px, 20px, 24px)
- `FontSize` constants: `SMALL=18`, `MEDIUM=20`, `LARGE=24`
- `get_font_renderer()` factory selects renderer based on `config.text_renderer`

**[render.py](render.py)** - Rendering functions
- `render()` orchestrates the complete display layout (current weather + daily forecast)
- `render_weather()` renders weather data with icons, temperature, and description
- Uses `DisplayController` with render flags for positioning and layout

**[weather.py](weather.py)** - Weather API integration and caching
- Fetches from OpenWeather OneCall API 3.0 (returns current + daily forecast)
- `lookup_geocoding()` converts zip/postcode and country code to lat/lon using OpenWeather Geocoding API
- Implements file-based caching in `cache/` directory with timestamp validation
- `Weather` and `Temperature` are simple data classes (no `@dataclass`, manual serialization)
- Maps weather condition titles to icon names

**[net.py](net.py)** - WiFi connection management
- Simple connect/disconnect functions for `network.WLAN`
- Connection blocks until successful

**[utils.py](utils.py)** - Utility functions
- `format_date()` for timestamp formatting (manual month name mapping - no `strftime`)
- `wrap_text()`, `sentence_join()`, `truncate_lines()` for text processing
- File/directory existence helpers (MicroPython `os.stat()` based)

**[images.py](images.py)** - Weather icon rendering
- Hardcoded 32x32 framebuffer data for weather icons (cloud, fog, lightning, rain, snow, sun)
- `show_image()` blits icon framebuffers to display at specified coordinates

**Hardware drivers** (in `epd/` directory)
- Manufacturer-provided drivers for Waveshare e-paper displays
- Different interfaces: large has separate `imageblack` framebuffer, small IS a framebuffer
- Generally shouldn't need modification unless supporting new display hardware

### Data Flow

1. **Initialization**: `read_config()` → `get_epd()` creates `Screen` → wrap in `PaddedScreen` (if configured) → wrap in `BufferedScreen` → `get_font_renderer()` → create `DisplayController`
2. **Fetch phase**: Check cache → connect to WiFi if needed → lookup geocoding (if zip/country specified) → call OpenWeather API → parse JSON → disconnect → cache results
3. **Render phase**: Enable virtual mode → `render()` uses `DisplayController` with render flags → `FontRenderer` renders text → disable virtual mode to flush buffered operations
4. **Sleep phase**: Deep sleep the display → sleep CPU for `refresh_mins` → loop

### Configuration

`config.txt` structure (key=value format):
- `ssid`, `password` - WiFi credentials
- **Location** (specify EITHER lat/lon OR zip/country):
  - `lat`, `lon` - Direct location coordinates for weather
  - `zip`, `country` - Zip/postcode and country code (e.g., `zip=E14`, `country=GB`). Automatically geocoded to lat/lon using OpenWeather Geocoding API
- `openweathermap_key` - API key
- `refresh_mins` - Main loop sleep duration (how often to update weather)
- `cache_mins` - How long cached API responses stay valid (reduces API calls)
- `display_size` - Either `small` or `large`
- `padding` - Optional display padding as `top,right,bottom,left` (e.g., `10,10,10,10`)
- `text_renderer` - Either `basic` (8x8 monospace) or `rich` (TrueType fonts). Defaults to `basic`

### Display Rendering Pattern

The rendering system uses bitwise flags to control behavior:
```python
from display import DisplayController
from font_renderer import FontSize

# Clear buffer, blank to white, render with thin padding
display.display_text(
    DisplayController.RENDER_FLAG_CLEAR | DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_THIN_PADDING,
    FontSize.MEDIUM,
    "NOW"
)

# Append to existing content without moving vertical cursor
display.display_right(
    DisplayController.RENDER_FLAG_APPEND_ONLY | DisplayController.RENDER_FLAG_NO_V_CURSOR,
    FontSize.SMALL,
    weather_date
)

# Just append and flush to display
display.display_text(
    DisplayController.RENDER_FLAG_FLUSH,
    FontSize.SMALL,
    "Text"
)
```

Common flag combinations:
- `CLEAR | BLANK` - Start fresh with white screen
- `APPEND_ONLY` - Don't clear, add to existing render
- `NO_V_CURSOR` - Don't advance vertical position (for same-line rendering)
- `FLUSH` - Push framebuffer to e-paper display immediately

### Important Files Not to Deploy

The root directory `.py` files get deployed to the Pico W. Files in `scripts/`, `attic/`, `docs/`, and the virtual environment should NOT be uploaded to the device. The `epd/` directory contains hardware drivers that should be deployed.
