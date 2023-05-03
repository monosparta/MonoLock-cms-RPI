#!/usr/bin/python3

import paho.mqtt.client as mqtt
import re
import os
from Locker import Locker
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()

    _locker = Locker()

    mqtt_host= os.getenv("MQTT_HOST")
    mqtt_port= int(os.getenv("MQTT_PORT"))
    mqtt_username= os.getenv("MQTT_USERNAME")
    mqtt_passsword= os.getenv("MQTT_PASSWORD")

    serial_port = os.getenv("SERIAL_PORT")

    def publish_unlock_status(id, error):
        client.publish('locker/unlock', payload=f'{id},{error}', qos=0, retain=False)

    def on_message(client, userdata, data):
        message = data.payload.decode()
        print("Received message " + message + " on topic '"
            + data.topic + "' with QoS " + str(data.qos))
        if not re.findall(r'^[\da-fA-F]{4}$', message):
            return
        
        if not _locker.unlock(message):
            publish_unlock_status(message, 1)
            return
        publish_unlock_status(message, 0)

    def on_connect(client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe("locker/unlock", qos=0)

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("Unexpected MQTT disconnection. Will auto-reconnect")


    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.username_pw_set(mqtt_username, mqtt_passsword)
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()
