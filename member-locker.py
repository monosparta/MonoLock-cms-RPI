#!/usr/bin/python3

import paho.mqtt.client as mqtt
import asyncio
import evdev
from evdev import categorize, ecodes
from evdev import UInput, InputDevice
from keyevent_reader import KeyEventReader
import serial.rs485


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


async def print_events(device):
    _keyevent_reader = KeyEventReader()
    print(_keyevent_reader.read_line(device))


# client = mqtt.Client()
# client.on_connect = on_connect
# client.connect("broker.emqx.io", 1883, 60)

# client.loop_forever()

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

# devices = [evdev.InputDevice('/dev/input/event0')]

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
                # client.publish('raspberry/topic', payload=barcode, qos=0, retain=False)
                print(barcode)
                ser = serial.rs485.RS485(port='/dev/ttyS0', baudrate=9600)
                ser.rs485_mode = serial.rs485.RS485Settings(False, True)
                if barcode == '000':
                    print("error!")

                elif barcode == '0123456789':
                    # 1 1
                    ser.write(b'\x8a\x01\x01\x11\x9b')

    except Exception as e:
        print(e)
    finally:
        try:
            device.ungrab()
        except Exception as e:
            pass
