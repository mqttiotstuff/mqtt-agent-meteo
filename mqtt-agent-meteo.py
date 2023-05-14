
#
# MQTT agent to manage a LED strip, with smooth transitions
#
#



import paho.mqtt.client as mqtt
import random
import time
import re
import configparser
import os.path
import traceback

config = configparser.RawConfigParser()


METEO = "home/agents/meteo"
DETECTOR = "home/esp05/sensors/meteo"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(DETECTOR)



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

   global METEO

   if msg.topic == DETECTOR:
      try:
         payload = msg.payload.decode("utf-8")
         m = re.match("T(\d+.?\d+),H(\d+.?\d+),P(\d+.?\d+)",payload)
         if m:
            (temperature,humidity,pression) = m.group(1),m.group(2),m.group(3) 
            client2.publish(METEO + "/temperature",temperature)
            client2.publish(METEO + "/humidity",humidity)
            client2.publish(METEO + "/pression",pression)
      except Exception as e:
         traceback.print_exc(e) 
         pass



#############################################################
## MAIN

conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
   raise Exception("config file " + conffile + " not found")

config.read(conffile)



username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")



client = mqtt.Client()
client2 = mqtt.Client()


client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username, password)
client.connect(mqttbroker, 1883, 60)

# client2 is used to send time oriented messages, without blocking the receive one
client2.username_pw_set(username, password)
client2.connect(mqttbroker, 1883, 60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client2.loop_start()
client.loop_start()

while True:
    time.sleep(2)
    client2.publish(METEO + "/healthcheck", "1")


