#!/usr/bin/env bash

DEVICE_PORT=$( ls /dev/cu.usbmodem14* )

ROOT_DIR=$(git rev-parse --show-toplevel)

python3 ./scripts/microdelete.py \
  -v \
  "$DEVICE_PORT"
