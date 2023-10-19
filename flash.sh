#!/bin/bash

#esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
#esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 $1
#esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 verify_flash 0x1000 $1

esptool.py --chip esp8266 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp8266 --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 $1
esptool.py --chip esp8266 --port /dev/ttyUSB0 --baud 460800 verify_flash --flash_size=detect 0 $1
