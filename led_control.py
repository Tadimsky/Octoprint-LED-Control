#!/usr/bin/env python

import argparse
import sys
import time
import os
import signal
import paho.mqtt.client as mqtt
from neopixel import *

from animations import *

# LED strip configuration:
LED_COUNT      = 47      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

class LEDControl():
    def __init__(self):
        self.strip = self.init_ledstrip()
        self.mqtt_client = mqtt.Client()

    def init_ledstrip(self):
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

    def init_mqtt(self):
        self.mqtt_client.username_pw_set('octoprint', password='alumaker3d')
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.mqtt_client.connect('raspi2.lan.r00t.ca', 1883, 60)

        self.mqtt_client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print('MQTT Client connected: {}'.format(rc))

        client.subscribe('octoprint/#')

    def on_message(self, client, userdata, msg):
        print(dir(msg))
        print('{0}: {1}'.format(msg.topic, msg.payload))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--daemon', help='Start LED Control Daemon.', nargs='?', const=True)
    parser.add_argument('--color', metavar='RGB', nargs=3, type=int)
    parser.add_argument('--color2', metavar='RGB', nargs=3, type=int)
    parser.add_argument('--animation', choices=ANIMATIONS.keys())
    parser.add_argument('--wait-ms', type=int, nargs=1)
    parser.add_argument('--interval', type=int, nargs=1)

    args = parser.parse_args()

    if args.daemon:
        try:
            ledcontrol = LEDControl()
            ledcontrol.init_mqtt()
        except Exception as e:
            print(e)
        finally:
            sys.exit(0)

    animation = ANIMATIONS[args.animation]
    os.setpgrp() # create new process group, become its leader
    try:
        color = Color(args.color[0], args.color[1], args.color[2])
        #color2 = Color(args.color2[0], args.color2[1], args.color2[2])
        animation(strip, color, iterations=args.interval)
    except Exception as e:
        print(e)
        er = sys.exc_info()[0]
        write_to_page( "<p>Error: %s</p>" % er )
    finally:
        sys.exit(0)