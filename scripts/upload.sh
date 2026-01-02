#!/usr/bin/env bash

DEVICE_PORT=$( ls /dev/cu.usbmodem* 2>/dev/null )

if [ -z "$DEVICE_PORT" ]; then
  echo "Error: No device found at /dev/cu.usbmodem*" >&2
  echo "Please check that your MicroPython device is connected." >&2
  exit 1
fi

ROOT_DIR=$(git rev-parse --show-toplevel)

if [[ $# -eq 0 ]]; then
  FILES_TO_UPLOAD=$(ls *.py)
  FILES_TO_UPLOAD+=" $(ls epd/*.py)"
  FILES_TO_UPLOAD+=" $(ls fonts/*.py)"
  FILES_TO_UPLOAD+=" config.txt"
else
  FILES_TO_UPLOAD="$@"
fi

python3 ./scripts/microupload.py \
  -v \
  -C "$ROOT_DIR" \
  "$DEVICE_PORT"  $FILES_TO_UPLOAD
