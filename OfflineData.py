#!/usr/bin/python3

import paho.mqtt.client as mqtt
import os
import sys
from MonoLock import MonoLock

from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()

    _monoLock = MonoLock(False)

    mqtt_host= os.getenv("MQTT_HOST")
    mqtt_port= int(os.getenv("MQTT_PORT"))
    mqtt_username= os.getenv("MQTT_USERNAME")
    mqtt_passsword= os.getenv("MQTT_PASSWORD")

    def publish_sync_status(error, mode='auto'):
        client.publish(os.getenv('MQTT_TOPIC_PREFIX', 'locker') + '/offline', payload=f'{mode},{error}', qos=0, retain=False)

    client = mqtt.Client()

    client.username_pw_set(mqtt_username, mqtt_passsword)

    if len(sys.argv) == 1 or sys.argv[1] != '--update-now':
        def on_message(client, userdata, data):
            message = data.payload.decode()
            print(f"[OfflineData/MQTT] Received message {message} on topic '{data.topic}' with QoS {data.qos}")
            if message != 'sync':
                return
            
            print('[OfflineData] Updating offline data...')
            sync_success = _monoLock.get_offline_data()
            print(f"[OfflineData] Sync {'Success' if sync_success else 'Failed'}")
            publish_sync_status(0 if sync_success else 1, 'manual')

        def on_connect(client, userdata, flags, rc):
            print(f"[OfflineData/MQTT] Connected with result code {rc}")
            client.subscribe(os.getenv('MQTT_TOPIC_PREFIX', 'locker') + "/offline", qos=0)

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("[OfflineData/MQTT] Unexpected MQTT disconnection. Will auto-reconnect")


        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.connect(mqtt_host, mqtt_port, 60)

        client.loop_forever()
    else:
        print('[OfflineData] Updating offline data...')
        sync_success = _monoLock.get_offline_data()
        print(f"[OfflineData] Sync {'Success' if sync_success else 'Failed'}")

        try:
            client.connect(mqtt_host, mqtt_port, 60)
            publish_sync_status(0 if sync_success else 1)
        except Exception as e:
            print(f"[MQTT] Connection failed: [{type(e)}] {e}")
        sys.exit(0)
