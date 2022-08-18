#!/usr/bin/python3

from array import array
from lib2to3.pgen2 import token
from time import sleep
import paho.mqtt.client as mqtt
import asyncio
import serial.rs485
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

mqtt_host= os.getenv("MQTT_HOST")
mqtt_port= int(os.getenv("MQTT_PORT"))
mqtt_username= os.getenv("MQTT_USERNAME")
mqtt_passsword= os.getenv("MQTT_PASSWORD")
serial_port = os.getenv("SERIAL_PORT")

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
            if( len(lockstatus) > 0 and check(lockstatus) == 0 ):
                return lockstatus
        except Exception as e:
            print(e)

        sleep(0.5)

def pub(msg):
    client.publish('locker/unlock', payload=msg,
                   qos=0, retain=False)

def on_message(client, userdata, data):
    message = data.payload.decode()
    print("Received message " + message + " on topic '"
          + data.topic + "' with QoS " + str(data.qos))
    if not re.findall(r'^[\da-fA-F]{4}$', message):
        return 0
    # data = ['8a', '01', '01', '11']
    data = ['8a', message[0:2], message[2:4], '11']

    checksum = check(data)

    data.extend([f'{hex(checksum)}'.lstrip('0x')])
    msg = bytes.fromhex("".join(data))
    for i in range(3):
        lockstatus = writeRS485Msg(msg)
        print(lockstatus)
        if(lockstatus[3] == '00'):
            pub(message + ",0")
            break
        sleep(0.5)
        if(i==2):
            pub(message + ",1")
    return 0

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_disconnect(client, userdata, flags):
    print("disconnect")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.username_pw_set(mqtt_username, mqtt_passsword)
client.connect(mqtt_host, mqtt_port, 60)
client.subscribe("locker/unlock", qos=0)
client.loop_forever()
