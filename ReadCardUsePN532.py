#!/usr/bin/python3

import json
from py532lib.i2c import Pn532_i2c
from time import sleep
import paho.mqtt.client as mqtt
import serial.rs485
import requests
import re
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("TOKEN")
sever_host = os.getenv("SERVER_HOST")
sever_port = ""
if(os.getenv("SERVER_PORT")):
    sever_port = ":" + os.getenv("SERVER_PORT")
sever_port = os.getenv("SERVER_PORT")
mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_passsword = os.getenv("MQTT_PASSWORD")

pn532 = Pn532_i2c()
pn532.SAMconfigure()


def makeRS485Msg(lockerEncoding):
    data = ['8a', lockerEncoding[0:2], lockerEncoding[2:4], '11']
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
    i = 5
    while i:
        try:
            ser = serial.rs485.RS485(port='/dev/ttyUSB0', baudrate=9600)
            ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            ser.timeout = 2
            ser.flushInput()  # flush input buffer
            ser.flushOutput()  # flush output buffer
            ser.write(msg)
            lockstatus = re.findall(r'.{2}', ser.read(5).hex())
            ser.close()
            print(lockstatus, "write")
            if(len(lockstatus) > 0 and check(lockstatus) == 0):
                return lockstatus
        except Exception as e:
            print(e)
            try:
                ser.close()
            except Exception as e:
                pass

        i -= 1
        sleep(0.5)
    return 1


def publish(msg, status):
    client = mqtt.Client()
    client.username_pw_set(mqtt_username, mqtt_passsword)
    client.connect(mqtt_host, mqtt_port, 60)
    client.publish('locker/error', payload=f'{msg}, {status}',
                   qos=0, retain=False)
    client.disconnect()
    if status == 1:
        print("error")


if __name__ == '__main__':
        while True:
            cardData = pn532.read_mifare().get_data()[7:11]
            hexData = ""
            for data in cardData:
                hexData = hex(data)[2:].zfill(2) + hexData
            barcode = str(int(hexData, 16)).zfill(10)
            if barcode is not None and len(barcode) > 0:
                print(barcode)
                res = requests.post(
                    sever_host + sever_port + '/api/RPIunlock',
                    headers={'token': token},
                    data={"cardId": barcode}
                )
                if(res.status_code >= 400):
                    print(json.loads(res.text))
                    continue

                print(res.text)
                msg = makeRS485Msg(res.text)
                lockstatus = writeRS485Msg(msg)
                if(lockstatus == 1 or lockstatus[3] != '00'):
                    publish(res.text, 1)
                    continue
                publish(res.text, 0)
                print(lockstatus[3])
                print("ok")
