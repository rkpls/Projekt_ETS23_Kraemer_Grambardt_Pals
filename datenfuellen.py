import gc
from machine import Pin, PWM, SoftI2C, I2S, unique_id, reset
from utime import ticks_ms, ticks_diff, sleep_ms, localtime
import asyncio

import network
from ubinascii import hexlify
from umqtt.simple import MQTTClient
import json
import neopixel
"""
from bme280_float import BME280
from bh1750 import BH1750
import CCS811
import sh1106
"""
# ---------- STATIC VARS ----------
ssid = 'BZTG-IoT'                                           #Schulwlan
password = 'WerderBremen24'
wlan = network.WLAN(network.STA_IF)
MQTT_SERVER = 'broker.hivemq.com'
CLIENT_ID = hexlify(unique_id())
MQTT_TOPIC = 'sensorwerte/*'
loop = asyncio.get_event_loop()

data_b = 420
data_t = 69
data_h = 4200
data_p = 420
data_c = 420
data_n = 69

def connect_wifi():                                         #fn für WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print(wlan.ifconfig())
    return wlan

def mqtt_send():                                              #schleife zum senden der Daten 
    global CLIENT_ID, MQTT_SERVER, MQTT_TOPIC
    passed = 0
    interval = 5000
    client = MQTTClient(CLIENT_ID, MQTT_SERVER)
    while True:
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):                   #schleife wird alle 5 Sekunden durchlaufen
            client.connect()
            werte = {
                'Bright': round(data_b,0),
                'Temp': round(data_t,1),
                'Humid': round(data_h,1),
                'Baro': round(data_p,0),
                'Carbon': round(data_c,0),
                'Noise': round(data_n,0),
                }
            dump = json.dumps(werte)                                #json formatieren und versenden
            client.publish(MQTT_TOPIC, dump)
            print(dump)
            client.disconnect()
            gc.collect()
            passed = time
        await asyncio.sleep_ms(10)
        

connect_wifi()

mqtt_send()
