#!/usr/bin/env bash

DEVICE_PORT=$( ls /dev/cu.usbmodem* 2>/dev/null )

if [ -z "$DEVICE_PORT" ]; then
  echo "Error: No device found at /dev/cu.usbmodem*" >&2
  echo "Please check that your MicroPython device is connected." >&2
  exit 1
fi

ROOT_DIR=$(git rev-parse --show-toplevel)

python3 ./scripts/microdelete.py \
  -v \
  "$DEVICE_PORT"
