#mqtt_publisher.py: publishes predicted tone to RPi LED via MQTT


import paho.mqtt.client as mqtt
import time


RPI_IP = "YOUR_RPI_IP_HERE"   # e.g. "192.168.1.45"
PORT   = 1883
TOPIC  = "led/tone"


#executed when successfully connects to MQTT broker, rc = 0 means connecion accepted
def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))

#publishes tone string to RPi, returns true if sent successfully
def publish_tone(tone: str) -> bool:

    #valid tones
    valid_tones = {"chill", "warm", "dark", "dance"}
    if tone not in valid_tones:
        print("Invalid tone: " + tone)
        return False

    # create a client object
    client = mqtt.Client()

    # attach the on_connect callback 
    client.on_connect = on_connect

    # connect to the MQTT broker running on the RPi
    client.connect(host=RPI_IP, port=PORT, keepalive=60)

    # background thread to handle sending and receiving  messages
    client.loop_start()

    time.sleep(1)

    # publish the tone to the topic the RPi is subscribed to
    # qos=1 means the broker will confirm before we continue
    client.publish(TOPIC, tone, qos=1)
    print("Published tone: " + tone + TOPIC)

    # stop the background thread and close the connection cleanly
    client.loop_stop()
    client.disconnect()
    return True

#test code: # send all 4 tones one by one to verify the LED changes color correctly
if __name__ == "__main__":

    for tone in ["chill", "warm", "dark", "dance"]:
        print("\nSending: " + tone.upper())
        publish_tone(tone)
        time.sleep(3)   # hold each color for 3 seconds before sending the next