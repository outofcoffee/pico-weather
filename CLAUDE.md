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

1. Copy `config.txt.example` to `config.txt` and fill in WiFi credentials, location coordinates, and OpenWeather API key
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

**[main.py](main.py)** - Entry point and orchestration
- `main()` runs the infinite loop: init display → fetch weather → render → sleep → repeat
- `fetch()` handles caching logic and network connection lifecycle
- `render()` and `render_weather()` compose the display layout

**[weather.py](weather.py)** - Weather API integration and caching
- Fetches from OpenWeather OneCall API 3.0 (returns current + daily forecast)
- Implements file-based caching in `cache/` directory with timestamp validation
- `Weather` and `Temperature` are simple data classes (no `@dataclass`, manual serialization)
- Maps weather condition titles to icon names

**[display.py](display.py)** - Display abstraction layer
- `DisplayWrapper` provides unified interface for different e-paper displays
- `EPD_7in5_B_Wrapper` for large 7.5" display
- `EPD_2in13_V3_Wrapper` for small 2.13" display
- `get_epd()` factory function selects display based on config
- Handles padding configuration (configurable via `config.txt`)

**[display_large.py](display_large.py)** and **[display_small.py](display_small.py)**
- Manufacturer-provided drivers for Waveshare e-paper displays
- Different interfaces: large has separate `imageblack` framebuffer, small IS a framebuffer
- Generally shouldn't need modification unless supporting new display hardware

**[render.py](render.py)** - Display controller with render flags
- `DisplayController` manages text rendering, cursor position, and layout
- Uses bit flags for render options (e.g., `RENDER_FLAG_CLEAR`, `RENDER_FLAG_APPEND_ONLY`, `RENDER_FLAG_FLUSH`)
- `last_text_y` tracks vertical cursor position for sequential rendering
- `CHAR_WIDTH = 8` pixels (monospace font)
- `get_max_text_width()` calculates character capacity based on display width minus padding

**[net.py](net.py)** - WiFi connection management
- Simple connect/disconnect functions for `network.WLAN`
- Connection blocks until successful

**[utils.py](utils.py)** - Utility functions
- `Config` class and `read_config()` for parsing `config.txt`
- `format_date()` for timestamp formatting (manual month name mapping - no `strftime`)
- `wrap_text()`, `sentence_join()`, `truncate_lines()` for text processing
- File/directory existence helpers (MicroPython `os.stat()` based)

**[images.py](images.py)** - Weather icon rendering
- Hardcoded 32x32 framebuffer data for weather icons (cloud, fog, lightning, rain, snow, sun)
- `show_image()` blits icon framebuffers to display at specified coordinates

### Data Flow

1. **Fetch phase**: Check cache → connect to WiFi if needed → call OpenWeather API → parse JSON → disconnect → cache results
2. **Render phase**: Build display layout with render flags → position text and icons → flush to e-paper display
3. **Sleep phase**: Deep sleep the display → sleep CPU for `refresh_mins` → loop

### Configuration

`config.txt` structure (key=value format):
- `ssid`, `password` - WiFi credentials
- `lat`, `lon` - Location coordinates for weather
- `openweathermap_key` - API key
- `refresh_mins` - Main loop sleep duration (how often to update weather)
- `cache_mins` - How long cached API responses stay valid (reduces API calls)
- `display_size` - Either `small` or `large`
- `padding` - Optional display padding as `top,right,bottom,left` (e.g., `10,10,10,10`)

### Display Rendering Pattern

The rendering system uses bitwise flags to control behavior:
```python
# Clear buffer, blank to white, render with thin padding
display.display_text(
    DisplayController.RENDER_FLAG_CLEAR | DisplayController.RENDER_FLAG_BLANK | DisplayController.RENDER_FLAG_THIN_PADDING,
    "NOW"
)

# Append to existing content without moving vertical cursor
display.display_right(
    DisplayController.RENDER_FLAG_APPEND_ONLY | DisplayController.RENDER_FLAG_NO_V_CURSOR,
    weather_date
)

# Just append and flush to display
display.display_text(DisplayController.RENDER_FLAG_FLUSH, "Text")
```

Common flag combinations:
- `CLEAR | BLANK` - Start fresh with white screen
- `APPEND_ONLY` - Don't clear, add to existing render
- `NO_V_CURSOR` - Don't advance vertical position (for same-line rendering)
- `FLUSH` - Push framebuffer to e-paper display immediately

### Important Files Not to Deploy

The `display_*.py` files and `images.py` contain all the display driver code. The root directory `.py` files get deployed to the Pico W. Files in `scripts/`, `attic/`, `docs/`, and the virtual environment should NOT be uploaded to the device.
