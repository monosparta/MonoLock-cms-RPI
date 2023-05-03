#!/usr/bin/python3

from time import sleep
import paho.mqtt.client as mqtt
import serial.rs485
import evdev
from KeyeventReader import KeyEventReader
import requests
import re
import os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("TOKEN")
sever_host = os.getenv("SERVER_HOST")
sever_port = os.getenv("SERVER_PORT")
if(sever_port != ""):
    sever_port = ":" + sever_port

mqtt_host= os.getenv("MQTT_HOST")
mqtt_port= int(os.getenv("MQTT_PORT"))
mqtt_username= os.getenv("MQTT_USERNAME")
mqtt_passsword= os.getenv("MQTT_PASSWORD")
serial_port = os.getenv("SERIAL_PORT")

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

_KeyEventReader = KeyEventReader()

def makeRS485Msg(lockerEncoding):
    # data = ['8a', '01', '01', '11']
    data = ['8a', lockerEncoding[1:3], lockerEncoding[3:5], '11']
    checksum = check(data)
    data.extend([f'{hex(checksum)}'.lstrip('0x')])
    msg = bytes.fromhex("".join(data))
    return msg

def check(data):
    checksum = 0
    for i in data:
        if(checksum == 0):
            checksum = int(i, 16)
        else:
            checksum = checksum ^ int(i, 16)
    return checksum

def writeRS485Msg(msg):
    while 1:
        try:
            ser = serial.rs485.RS485(port=serial_port, baudrate=9600)
            ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            ser.timeout = 2
            ser.flushInput()  # flush input buffer
            ser.flushOutput()  # flush output buffer
            ser.write(msg)
            lockstatus = re.findall(r'.{2}', ser.read(5).hex())
            ser.close()
            print(lockstatus,"write")
            if( len(lockstatus) > 0 and check(lockstatus) == 0 ):
                return lockstatus
        except Exception as e:
            print("error",e)
            try:
                ser.close()
            except Exception as e:
                pass

        sleep(0.5)
  
def pub(msg):
    client = mqtt.Client()
    client.username_pw_set(mqtt_username, mqtt_passsword)
    client.connect(mqtt_host, mqtt_port, 60)
    client.publish('locker/error', payload=msg,
                   qos=0, retain=False)
    client.disconnect()

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
            barcode = _KeyEventReader.read_line(device)
            if barcode is not None and len(barcode) > 0:
                print(barcode)
                res = requests.post(
                    sever_host + sever_port +'/api/RPIunlock',
                    headers={'token': token},
                    data={"cardId": barcode}
                )
                print(res.text)
                if(res.status_code>=400):
                    continue

                msg = makeRS485Msg(res.text)
                for i in range(3):
                    lockstatus = writeRS485Msg(msg)
                    print(lockstatus[3])
                    if(lockstatus[3] == '00'):
                        break
                    sleep(0.5)
                    if(i==2):
                        pub(res.text)
                print("break")
    except Exception as e:
        print(e)
    finally:
        try:
            device.ungrab()
        except Exception as e:
            pass
    