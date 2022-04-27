#!/usr/bin/python3

from array import array
from lib2to3.pgen2 import token
from time import sleep
import paho.mqtt.client as mqtt
import asyncio
import serial.rs485
import requests


def on_message(client, userdata, data):
    message = data.payload.decode()
    print("Received message " + message + " on topic '"
          + data.topic + "' with QoS " + str(data.qos))
    # data = ['8a', '01', '01', '11']
    data = ['8a', message[0:2], message[2:4], '11']

    checksum = 0
    for i in data:
        if(checksum == 0):
            checksum = int(i, 16)
        else:
            checksum = checksum ^ int(i, 16)

    data.extend([f'{hex(checksum)}'[2:4]])
    msg = bytes.fromhex("".join(data))
    print('input:', msg)

    while 1:
        try:
            ser = serial.rs485.RS485(port='COM3', baudrate=9600)
            ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            ser.write(msg)
            print('output:', ser.read(5))
            ser.close()
            break
        except Exception as e:
            print(e)
            i+=1
            sleep(0.5)



def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("pi", "00010000")
client.connect("127.0.0.1", 1883, 60)
client.subscribe("locker/unlock", qos=0)
client.loop_forever()
