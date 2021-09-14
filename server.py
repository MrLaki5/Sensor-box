import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, escape
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import logging
import json
from threading import Thread
import datetime

logging.basicConfig(level=logging.INFO)
active_devices_info = {}
mqtt_thread = None

application = Flask(__name__, template_folder='.')


class MQTT_Thread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.stop = False

	def run(self):
		while not self.stop and client.loop_forever() == 0:
			pass
		logging.info("MQTT: Thread terminated")

socketio = SocketIO(application, cors_allowed_origins="*")

@socketio.on('connect')
def connect():
    socketio.emit("device_info", data=json.dumps(active_devices_info))

def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("devices/active_report", qos=1)
        client.subscribe("devices/offline_report", qos=1)
    else:
        logging.error("MQTT: bad connection, result code: " + str(rc))

def handle_disconnect(client, userdata, rc):
    logging.info("MQTT: disconnecting from broker: " + str(rc))

def handle_subscribe(client, userdata, mid, granted_qos):
    logging.info("MQTT: subscribed to channel result code " + str(mid))

def handle_mqtt_message(client, userdata, message):
    curr_device = message.payload.decode("UTF-8")
    # If message is from active, add camera id to active set, else remove it from set
    if message.topic == "devices/active_report":
        curr_device_info = json.loads(curr_device)
        curr_device = escape(curr_device_info["box_id"])
        if curr_device not in active_devices_info:
            active_devices_info[escape(curr_device_info["box_id"])] = {}
        utc_current_time = datetime.datetime.utcnow()
        active_devices_info[escape(curr_device_info["box_id"])]["Time"] = utc_current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        active_devices_info[escape(curr_device_info["box_id"])]["PM10"] = escape(curr_device_info["PM10"])
        active_devices_info[escape(curr_device_info["box_id"])]["PM2.5"] = escape(curr_device_info["PM2.5"])
        active_devices_info[escape(curr_device_info["box_id"])]["Temp"] = escape(curr_device_info["Temp"])
        active_devices_info[escape(curr_device_info["box_id"])]["Humidity"] = escape(curr_device_info["Humidity"])
    elif message.topic == "devices/offline_report":
        active_devices_info.pop(curr_device, None)
    # Publish retain message of refreshed active users
    socketio.emit("device_info", data=json.dumps(active_devices_info))
    logging.info("MQTT: message received, channel: " + message.topic + ", message: " + str(message.payload))

@application.route('/')
def index():
    logging.info("INDEX called")
    return render_template("index.html")



client = mqtt.Client(client_id="61c911fa-a67d-49a4-adf2-010844f84eec")
client.on_connect = handle_connect
client.on_message = handle_mqtt_message
client.on_disconnect = handle_disconnect
client.on_subscribe = handle_subscribe
client.connect("0.0.0.0", port=1883, keepalive=60)



if __name__ == '__main__':
    try:
        mqtt_thread = MQTT_Thread()
        mqtt_thread.start()
        socketio.run(application, host='192.168.1.104', port=5000, use_reloader=False, debug=True)
    except Exception as ex:
        client.disconnect()
