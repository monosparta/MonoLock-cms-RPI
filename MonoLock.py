import os
import requests
import json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv


class MonoLock:
    def __init__(self) -> None:
        load_dotenv()
        self.__mqtt_host = os.getenv("MQTT_HOST")
        self.__mqtt_port = int(os.getenv("MQTT_PORT"))
        self.__mqtt_username = os.getenv("MQTT_USERNAME")
        self.__mqtt_passsword = os.getenv("MQTT_PASSWORD")

        self.__token = os.getenv("TOKEN")
        self.__sever_host = os.getenv("SERVER_HOST")
        self.__sever_port = os.getenv("SERVER_PORT")
        if (self.__sever_port != ""):
            self.__sever_port = ":" + self.__sever_port

    def publish_error(self, id, error):
        client = mqtt.Client()
        client.username_pw_set(self.__mqtt_username, self.__mqtt_passsword)
        client.connect(self.__mqtt_host, self.__mqtt_port, 60)
        client.publish('locker/error', payload=f'{id}, {error}', qos=0, retain=False)
        client.disconnect()
        print(f"[MQTT] Sent ID: {id} Error: {error}")

    def get_id(self, card_number):
        res = requests.post(
            self.__sever_host + self.__sever_port + '/api/RPIunlock',
            headers={'token': self.__token},
            data={"cardId": card_number}
        )
        if (res.status_code >= 400):
            print(f"[Request] Status: {res.status_code} Body: {json.loads(res.text)}")
            print(f"[MonoLock] Could find locker id by {card_number}")
            return
        lock_id = res.text.replace('"', '')
        print(f"[MonoLock] Found {card_number} -> {lock_id}")
        return lock_id
