import serial
import json
import paho.mqtt.client as mqtt
from threading import Thread
import logging

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
ser.flush()

mqtt_thread = None

class MQTT_Thread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.stop = False

	def run(self):
		while not self.stop and client.loop_forever() == 0:
			pass
		logging.info("MQTT: Thread terminated")


client = mqtt.Client(client_id="sensor-1", clean_session=True)
client.will_set("devices/offline_report", "sensor-1", qos=1)

client.connect("0.0.0.0", port=1883, keepalive=60)
mqtt_thread = MQTT_Thread()
mqtt_thread.start()

while True:
	if ser.in_waiting > 0:
		line = ser.readline().decode("utf-8").rstrip()
		json_line = json.loads(line)
		json_line["box_id"] = "sensor-1"
		client.publish("devices/active_report", json.dumps(json_line), qos=1)
		print(json.dumps(json_line, indent=4))
