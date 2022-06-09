#!/usr/bin/python3

from array import array
# from asyncio.windows_events import NULL
from re import S
from socket import timeout
import paho.mqtt.client as mqtt
import asyncio
import serial.rs485
import requests
import re
from time import sleep
import os
from dotenv import load_dotenv
load_dotenv()

mqtt_host= os.getenv("MQTT_HOST")
mqtt_port= int(os.getenv("MQTT_PORT"))
boardNum = int(os.getenv("BOARD_NUM"))

# async def print_events(device):
#     _keyevent_reader = KeyEventReader()
#     print(_keyevent_reader.read_line(device))

def on_disconnect(client, userdata, flags):
    print("disconnect")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.username_pw_set("pi", "00010000")
client.connect(mqtt_host, mqtt_port, 60)

# # client.loop_forever()


def makeRS485Msg(lockerEncoding):
    data = ['80', lockerEncoding, '00', '33']
    checksum = check(data)
    data.extend([f'{hex(checksum)}'.lstrip('0x')])
    msg = bytes.fromhex(" ".join(data))
    return msg


def check(data):
    checksum = 0
    for i in data:
        if(checksum == 0):
            checksum = int(i, 16)
        else:
            checksum = checksum ^ int(i, 16)
    return checksum


def callStatus(msg):
    while 1:
        try:
            ser = serial.rs485.RS485(port='/dev/ttyUSB0', baudrate=9600)
            ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            ser.flushInput()  # flush input buffer
            ser.write(msg)
            ser.flushOutput()  # flush output buffer
            res = re.findall(r'.{2}', ser.read(7).hex())
            ser.close()
            return res
        except Exception as e:
            print(e)
            sleep(0.5)

def makeMqttMsg(board, data):
    bindata = format(int(data, 16), "08b")
    print(bindata)
    ans = []
    for i in range(8):
        if bindata[7-i] == '0':
            ans.append("{:s}{:s}".format(
                hex(board).lstrip('0x').zfill(2),
                hex(i+1).lstrip('0x').zfill(2)))
    return ans


def pub(msg):
    client.publish('locker/status', payload=",".join(msg),
                   qos=0, retain=False)


n = 1
while n:
    # n -= 1
    ans = []
    for i in range(1, boardNum+1):
        msg = makeRS485Msg(str(i).zfill(2))
        res = callStatus(msg)
        if(check(res) == 0):
            ans.extend(makeMqttMsg(i, res[4]))
    pub(ans)
    sleep(3)
