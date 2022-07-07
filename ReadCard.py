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
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("TOKEN")
sever_host = os.getenv("SERVER_HOST")
sever_port = ""
if(os.getenv("SERVER_PORT")):
    sever_port = ":" + os.getenv("SERVER_PORT")

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

_keyevent_reader = KeyEventReader()

for device in devices:

    print(device.info.vendor)
    print(device.info.product)

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
                    sever_host + sever_port +'/api/RPIunlock',
                    headers={'token': token},
                    data={"cardId": barcode}
                )
                print(res.text)
                print(res.status_code)
                if(res.status_code>=400):
                    continue
                # data = ['8a', '01', '01', '11']
                data = ['8a', res.text[0:2], res.text[2:4], '11']

                checksum = 0
                for i in data:
                    if(checksum == 0):
                        checksum = int(i, 16)
                    else:
                        checksum = checksum ^ int(i, 16)

                data.extend([f'{hex(checksum)}'[2:4]])
                msg = bytes.fromhex("".join(data))
                while 1:
                    try:
                        ser = serial.rs485.RS485(port='/dev/ttyUSB0', baudrate=9600)
                        ser.rs485_mode = serial.rs485.RS485Settings(False, True)
                        ser.flushInput()  # flush input buffer
                        ser.write(msg)
                        ser.flushOutput()  # flush output buffer
                        print('output:', ser.read(5))
                        ser.close()
                        break
                    except Exception as e:
                        print(e)
                        sleep(0.5)

    except Exception as e:
        print(e)
    finally:
        try:
            device.ungrab()
        except Exception as e:
            pass
