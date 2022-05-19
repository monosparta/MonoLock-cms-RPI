#!/usr/bin/python3

from array import array
# from lib2to3.pgen2 import token
from time import sleep
import paho.mqtt.client as mqtt
import asyncio
import serial.rs485
import evdev
from evdev import InputDevice
from keyevent_reader import KeyEventReader
import requests
import json
token = "hP4VspmxA6YtIltVtzXioPY3xixgrvxLTMpvkkefWpRjmgpRMdGZ1FtoWWNx"
url = "https://dd82-211-72-239-241.ngrok.io/"

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

_keyevent_reader = KeyEventReader()

for device in devices:

    if device.info.vendor != 0xffff or device.info.product != 0x0035:
        continue

    print(device.info)
    print(device.path, device.name, device.phys)

    try:
        device.grab()
        while True:
            barcode = _keyevent_reader.read_line(device)
            if barcode is not None and len(barcode) > 0:
                print(barcode)
                res = requests.post(
                    url+'api/unlock',
                    headers={'token': token},
                    data={"cardId": barcode}
                )
                print(res.text)
                print(res.status_code)

    except Exception as e:
        print(e)
    finally:
        try:
            device.ungrab()
        except Exception as e:
            pass
