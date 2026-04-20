#led_controller.py: subscribes to tone topic and sets RGB LED color 
#used ChatGPT to understand how to use RGBLED to handle PWM signals that can change colors

import paho.mqtt.client as mqtt
from gpiozero import RGBLED

# pin numbers 
RED_PIN   = 17
GREEN_PIN = 27
BLUE_PIN  = 22


#create RGB LED object, gpiozero handles PWM signals, colors set as tuples
led = RGBLED(red=RED_PIN, green=GREEN_PIN, blue=BLUE_PIN)


TONE_COLORS = {
    "chill": (0/255,   180/255, 200/255),   # teal
    "warm":  (255/255, 160/255,  40/255),   # yellow orange
    "dark":  (80/255,    0/255, 160/255),   # deep purple
    "dance": (220/255,  50/255,  50/255),   # ligher red
}



#when client receives connection from broker, subscribe to topic
def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))

    # subscribe to the topic that mqtt_publisher.py publishes to
    client.subscribe("led/tone")

    # register callback specifically for this topic
    client.message_callback_add("led/tone", on_message_from_tone)



#default callback for any message without custom callback, shouldn't fire
def on_message(client, userdata, msg):
    print("Default callback - topic: " + msg.topic + "   msg: " + str(msg.payload, "utf-8"))


# Custom callback for messages arriving on the "led/tone" topic
def on_message_from_tone(client, userdata, message):
    tone = message.payload.decode().strip().lower()
    print("Tone received: " + tone)

    if tone in TONE_COLORS:
        # set the LED to the RGB color mapped to this tone
        led.color = TONE_COLORS[tone]
        print("LED set to " + tone.upper())
    else:
        print("Unknown tone: " + tone + " — LED unchanged")


if __name__ == '__main__':

    # create a client object representing the RPi
    client = mqtt.Client()

    # attach the default message callback
    client.on_message = on_message

    # subscribe
    client.on_connect = on_connect

    #connect to broker running on RPi
    client.connect(host="localhost", port=1883, keepalive=60)

    client.loop_forever()