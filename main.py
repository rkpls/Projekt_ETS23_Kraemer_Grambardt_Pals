"""
ESP32-S3-DevKitC V4/MicroPython
Libraries / Info:
+ bme280 - https://github.com/robert-hh/BME280
+ bh1750 - https://github.com/flrrth/pico-bh1750
+ ccs811 - https://github.com/Notthemarsian/CCS811
+ inmp441 - https://docs.micropython.org/en/latest/library/machine.I2S.html
+ sh1106 - https://github.com/robert-hh/SH1106

Beschreibung: https://nds.edumaps.de/28168/79685/98e7g9w0dw

--- V2: 28.02.2024 ---
--- Jan Krämer, David Grambardt, Riko Pals ---

"""

import gc
from machine import Pin, PWM, SoftI2C,  unique_id
from utime import ticks_ms, ticks_diff, sleep_ms

import network
from ubinascii import hexlify
from umqtt.simple import MQTTClient
import json

from bme280_float import BME280
from bh1750 import BH1750
import CCS811
import sh1106

# ---------- CHANGABLE VARS ----------
ssid = 'BZTG-IoT'
password = 'WerderBremen24'
wlan = network.WLAN(network.STA_IF)
MQTT_SERVER = 'broker.hivemq.com'
CLIENT_ID = hexlify(unique_id())
MQTT_TOPIC = 'sensorwerte'

# ---------- DATA ----------
data_b = 0
data_t = 0
data_h = 0
data_p = 0
data_c = 0
data_d = 0

c = 0

# ---------- VARS ----------
bright = []
temp = []
humid = []
baro = []
cc = []
dB = []

passed_oled = 0
index_list = 0
passed_sensors = 0
passed_mqtt = 0

# ---------- PINS ----------
pin_SDA = 9
pin_SCL = 8

pin_Air = Pin.OUT(15)
pin_wled = 16

# ---------- I2C + SENSORS + OLED----------
i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)
bh1750 = BH1750(0x23, i2c)
bme280 = BME280(i2c=i2c)
ccs = CCS811.CCS811(i2c, addr=0x5a)
oled = sh1106.SH1106_I2C(128, 64, i2c, Pin(0), 0x3c)
oled.sleep(False)

# ----------- DEFS ----------

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print(wlan.ifconfig())
    return wlan

def average(values):
    if len(values) > 0:
        if len(values) > 8:
            values.pop(0)
        return sum(values) / len(values)
    else:
        return 1

def read_c(value):
    try:
        if ccs.data_ready():
            value = ccs.eCO2
        return value
    except Exception as e:
        print("Error:", e)


def oled_w():
    global passed_oled, index_list
    interval = 3000
    werte = [average(bright), average(temp), average(humid), average(baro), average(cc)]
    print(werte)
    time = ticks_ms()
    if (ticks_diff(time, passed_oled) > interval):
        wert = werte[index_list]
        oled.fill(0)
        oled.text(str(wert), 8, 24, 1)
        oled.show()
        index += 1
        if index_list >= len(werte):
            index_list = 0
    passed_oled = time


def sensors_read():
    global passed_sensors, bright, temp, humid, baro, cc, c, data_b, data_t, data_h, data_p, data_c
    interval = 500
    time = ticks_ms()
    if (ticks_diff(time, passed_sensors) > interval):
        b = bh1750.measurement
        bright.append(b)
        data_b = b
        t = bme280.value_t
        data_t = t
        temp.append(t)
        h = bme280.value_h
        data_h = h
        humid.append(h)
        p = bme280.value_p
        data_p = p
        baro.append(p)
        if ccs.data_ready():
            c = ccs.eCO2
            if c != 400:                #lesefehler (ausgabe 400) nicht übernehemen
                data_c = c
        cc.append(c)
    passed_sensors = time

def mqtt_send():
    global CLIENT_ID, MQTT_SERVER, MQTT_TOPIC, passed_mqtt
    time = ticks_ms()
    interval = 5000
    if (ticks_diff(time, passed_mqtt) > interval):
        client = MQTTClient(CLIENT_ID, MQTT_SERVER)
        client.connect()
        werte = {
            'Bright:': data_b,
            'Temp': data_t,
            'Humid': data_h,
            'Baro': data_p,
            'CCS': data_c,
            'dB': data_d,
            }
        dump = json.dumps(werte)
        print(str(dump))
        client.publish(MQTT_TOPIC, dump)
        client.disconnect()
    passed_mqtt = time

gc.collect()
connect_wifi()
while True:
    sensors_read()
    mqtt_send()
    oled_w()

