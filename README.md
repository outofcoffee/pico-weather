# Pico Weather Dashboard

A simple weather dashboard for the Pi Pico.

Fetches weather data from [OpenWeather](https://openweathermap.org/) and displays it on an e-paper display on the Pi Pico.

## Hardware

- [Raspberry Pi Pico W](https://www.raspberrypi.org/products/raspberry-pi-pico/)
- [Waveshare 2.13inch e-Paper HAT](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT)

## Dependencies

- MicroPython

## Setup

1. Clone the repository.
2. Copy `config.example.py` to `config.txt` and fill in the required values.
3. Copy the `config.txt` file to the Pi Pico.
4. Copy the Python files in the root directory to the Pi Pico.

Example:

```bash
$ python3 ./scripts/microupload.py -v /dev/cu.usbmodem14101 config.txt display.py main.py utils.py
```

## Running a REPL session

Install `mpremote` - MicroPython Remote Control:

```
pip install mpremote
```

Then to open a REPL session:

```
mpremote
```

To exit:
```
Ctrl-]
```

## Images

Weather icons by <a target="_blank" href="https://icons8.com">Icons8</a>.
