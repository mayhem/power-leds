#!/bin/bash

esptool.py --port /dev/ttyACM0 erase_flash
esptool.py --port /dev/ttyACM0 --baud 460800 --before default_reset --after hard_reset --chip esp32s3  write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 firmware.bin
