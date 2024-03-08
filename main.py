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
from machine import Pin, PWM, SoftI2C, I2S, unique_id, reset
from utime import ticks_ms, ticks_diff, sleep_ms
import asyncio

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

index_list = 0

# ---------- PINS ----------
pin_vent = PWM(Pin(15))
pin_SDA = 9
pin_SCL = 8
mic_data = Pin(6, Pin.IN)
mic_clk = Pin(5, Pin.IN)
mic_ws = Pin(4, Pin.IN)

# ---------- I2C + I2S + SENSORS + OLED----------
i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)

i2s = I2S(2,
            sck=mic_clk,
            ws=mic_ws,
            ss=mic_data,
            mode=I2S.RX,
            bits=16,
            format=I2S.MONO,
            rate=16000,
            ibuf=20000)

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
    
def read_peak():
    i2s.start()
    buffer = bytearray(256)
    i2s.readinto(buffer)
    peak = max(buffer)
    i2s.stop()
    return peak

async def oled_w():
    global index_list
    werte = [average(bright), average(temp), average(humid), average(baro), average(cc)]
    while True:
        wert = werte[index_list]
        oled.fill(0)
        oled.text(str(wert), 8, 24, 1)
        oled.show()
        index_list += 1
        if index_list >= len(werte):
            index_list = 0
        await asyncio.sleep_ms(3000)
    
async def sensors_read():
    global bright, temp, humid, baro, cc, c, dB, data_b, data_t, data_h, data_p, data_c, data_d
    while True:
        b = int(bh1750.measurement)
        bright.append(b)
        data_b = b
        t = round(bme280.value_t,1)
        data_t = t
        temp.append(t)
        h = round(bme280.value_h,1)
        data_h = h
        humid.append(h)
        p = int(bme280.value_p * 0.01)
        data_p = p
        baro.append(p)
        if ccs.data_ready():
            sleep_ms(10)
            c = ccs.eCO2
        cc.append(c)
        dB = read_peak()
        data_d = dB
        dB.append(dB)
        await asyncio.sleep_ms(200)

async def mqtt_send():
    global CLIENT_ID, MQTT_SERVER, MQTT_TOPIC
    while True:
        client = MQTTClient(CLIENT_ID, MQTT_SERVER)
        client.connect()
        werte = {
            'Bright': data_b,
            'Temp': data_t,
            'Humid': data_h,
            'Baro': data_p,
            'Carbon': data_c,
            'Noise': data_d,
            }
        dump = json.dumps(werte)
        print(str(dump))
        client.publish(MQTT_TOPIC, dump)
        client.disconnect()
        await asyncio.sleep_ms(2000)        

gc.collect()
connect_wifi()

loop = asyncio.get_event_loop()

pin_vent.freq(1000)
pin_vent.duty(1023)

try:
    loop.create_task(sensors_read())
    loop.create_task(mqtt_send())
    loop.create_task(oled_w())
    loop.run_forever()
except Exception as e:
    print("Error:", e)
finally:
    loop.close()
    sleep_ms(10000)
    reset()

