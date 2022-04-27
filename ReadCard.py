#!/usr/bin/python3

from array import array
# from lib2to3.pgen2 import token
from time import sleep
import paho.mqtt.client as mqtt
import asyncio
import serial.rs485
import requests
import json
token = ""
url = "https://dd82-211-72-239-241.ngrok.io/"
while 1:
    barcode = input("please input:")

    while 1:
        res = requests.post(
            url+'api/unlock',
            headers={'token': token},
            data={"cardId": barcode}
        )
        if(res.status_code == 401):
            r = requests.post(
                url+'api/login',
                data={
                    "email": "002@example.com",
                    "password": "pi"
                }
            )
            token = json.loads(r.text)["message"]["token"]
        if(res.status_code == 200 or res.status_code == 400):
            break

    print(res.text)
