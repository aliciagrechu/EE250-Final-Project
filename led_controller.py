#led_controller.py: subscribes to tone topic and sets RGB LED color 
#used ChatGPT to understand how to use RGBLED to handle PWM signals that can change colors

import paho.mqtt.client as mqtt
from gpiozero import LED

# Pin numbers — wire your red, yellow, and blue LEDs to these GPIO pins
RED_PIN    = 17
YELLOW_PIN = 27
BLUE_PIN   = 22

# Create three separate LED objects
led_red    = LED(RED_PIN)
led_yellow = LED(YELLOW_PIN)
led_blue   = LED(BLUE_PIN)

# Maps each tone to which LEDs should be on (red, yellow, blue)
TONE_LEDS = {
    "chill": (False, False, True),   # blue only
    "warm":  (False, True,  False),  # yellow only
    "dark":  (True,  False, False),  # red only
    "dance": (True,  True,  True),   # all three
}

def set_leds(red, yellow, blue):
    led_red.on()    if red    else led_red.off()
    led_yellow.on() if yellow else led_yellow.off()
    led_blue.on()   if blue   else led_blue.off()

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

    if tone in TONE_LEDS:
        r, y, b = TONE_LEDS[tone]
        set_leds(r, y, b)
        print("LED set for " + tone)
    else:
        print("Unknown tone: " + tone)

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