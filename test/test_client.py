import paho.mqtt.client as mqtt
import logging
import ssl
import json


logging.basicConfig(level=logging.INFO)
event_creator_uuid = "333a3843-6794-4f46-af2f-7133bcfd38d8"



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.info("Connected, result code  " + str(rc))
    test_json = {
            "box_id": "device-3", 
            "Temp": 24.5,
            "Humidity": 40,
            "PM2.5": 2500,
            "PM10": 1800
    }
    client.publish("devices/active_report", json.dumps(test_json), qos=1)
    client.disconnect()


def on_disconnect(client, userdata, rc):
    logging.info("Disconnecting reason  " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client_curr, userdata, msg):
    logging.info("Got message, topic: " + msg.topic + " message: " + msg.payload.decode("UTF-8"))


def on_subscribe(client, userdata, mid, granted_qos):
    logging.info("Subscribe, result code " + str(mid))


client = mqtt.Client(client_id=event_creator_uuid, clean_session=True)
client.will_set("devices/offline_report", event_creator_uuid, qos=1)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

try:
    client.connect("0.0.0.0", port=1883, keepalive=60)
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
except Exception as ex:
    logging.info("Connection was not established: " + str(ex))
