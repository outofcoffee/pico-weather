#!/usr/bin/env bash

DEVICE_PORT="/dev/cu.usbmodem14101"

ROOT_DIR=$(git rev-parse --show-toplevel)

python3 ./scripts/microdelete.py \
  -v \
  "$DEVICE_PORT"
