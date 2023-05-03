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

        if not os.path.exists('data/'):
            os.mkdir('data/')

        self.client = mqtt.Client()
        self.client.on_connect = self.__on_mqtt_connect
        self.client.on_disconnect = self.__on__mqtt_disconnect
        self.client.username_pw_set(self.__mqtt_username, self.__mqtt_passsword)
        self.__try_connect_mqtt()

    def __try_connect_mqtt(self):
        try:
            self.client.connect(self.__mqtt_host, self.__mqtt_port, 60)
        except Exception as e:
            print(f"[MQTT] Connection failed: [{type(e)}] {e}")


    def __on_mqtt_connect(client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def __on__mqtt_disconnect(client, userdata, rc):
        if rc != 0:
            print("Unexpected MQTT disconnection. Will auto-reconnect on next publish")

    def publish_error(self, id, error):
        if not self.client.is_connected():
            self.__try_connect_mqtt()
        self.client.publish('locker/error', payload=f'{id}, {error}', qos=0, retain=False)

    def publish_status(self, status):
        if not self.client.is_connected():
            self.__try_connect_mqtt()
        self.client.publish('locker/status', payload=status, qos=0, retain=False)
        
    def get_id(self, card_number):
        try:
            res = requests.post(
                self.__sever_host + self.__sever_port + '/api/RPIunlock',
                headers={'token': self.__token},
                data={"cardId": card_number}
            )
            if (res.status_code >= 400):
                print(f"[Request] Status: {res.status_code} Body: {json.loads(res.text)}")
                print(f"[MonoLock] Could not find locker id by {card_number}")
                return
            lock_id = res.text.replace('"', '')
        except requests.ConnectionError as e:
            print(f"[Request] Connection error: {e}")
            return self.__get_offline_id(card_number)
        print(f"[MonoLock] Found {card_number} -> {lock_id}")
        return lock_id

    def __get_offline_id(self, card_number):
        print("[MonoLock] Enter offline mode.")
        if not os.path.exists('data/locker.json') and not os.path.exists('data/member.json'):
            print("[MonoLock] No offline data found.")
            return

        with open('data/locker.json', 'r') as fs:
            locker = json.load(fs)

        with open('data/member.json', 'r') as fs:
            member = json.load(fs)

        if card_number == '000':
            print("[MonoLock/Offline] Card read fail")
            return

        if card_number not in member:
            print(f"[MonoLock/Offline] Could not find locker id by {card_number}")
            return

        locker_no = member[card_number]
        print(f"[MonoLock/Offline] Found {card_number} -> No. {locker_no}")
        if locker_no not in locker:
            print(f"[MonoLock/Offline] {locker_no} does not have a locker id")
            return
        locker_id = locker[locker_no]
        print(f"[MonoLock/Offline] Found No. {locker_no} -> {locker_id}")
        return locker_id
