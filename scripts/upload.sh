#!/usr/bin/env bash

DEVICE_PORT=$( ls /dev/cu.usbmodem* )

ROOT_DIR=$(git rev-parse --show-toplevel)

FILES_TO_UPLOAD=$(ls *.py)
FILES_TO_UPLOAD+=" config.txt"

python3 ./scripts/microupload.py \
  -v \
  -C "$ROOT_DIR" \
  "$DEVICE_PORT"  $FILES_TO_UPLOAD
