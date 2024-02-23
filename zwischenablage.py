import gc
import json
from machine import Pin, SoftI2C, unique_id
from utime import ticks_ms, ticks_diff, sleep_ms
import network
from ubinascii import hexlify
from umqtt.simple import MQTTClient

from bme280_float import BME280 as bme_280
import CCS811 as ccs_811
import bh1750 as bh_1750
import sh1106 as sh_1106

pin_scl = Pin(8)
pin_sda = Pin(9)
i2s_data_pin = 4
i2s_clk_pin = 5
i2s_ws_pin = 6
pin_vent = Pin(16, Pin.OUT)

i2c = SoftI2C(scl=pin_scl, sda=pin_sda, freq=1000000)

pin_vent.value(1)

bme280 = bme_280(i2c=i2c)
bh1750 = bh_1750(0x23, i2c)
ccs811 = ccs_811(i2c=i2c)
oled = sh_1106(128, 64, i2c, Pin(0), 0x3c) 

temp = []
humid = []
baro = []
bright = []
co2 = []

ssid = 'Telekom_Pals'
password = 'fk_afd!'
wlan = network.WLAN(network.STA_IF)
MQTT_SERVER = '192.168.2.41'
CLIENT_ID = hexlify(unique_id())
MQTT_TOPIC = 'KGP'

oled.sleep(False)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    return wlan

def average(values):
    if len(values) > 0:
        return sum(values) / len(values)
    else:
        return 1
    
def update_data():
    global temp, humid, baro, bright, co2
    temp.append(bme280.value_t)
    if len(temp) >= 5:
        temp.pop(0)
        temp = average(temp)
    humid.append(bme280.value_h)
    if len(humid) >= 5:
        humid.pop(0)
        humid = average(humid)
    baro.append(bme280.value_b)
    if len(baro) >= 5:
        baro.pop(0)
        baro = average(baro)
    bright.append(bh1750.measurement)
    if len(bright) >= 5:
        bright.pop(0)
        bright = average(bright)
    if ccs811.data_ready():
        co2.append(ccs811.eCO2)
        if len(co2) >= 5:
            co2.pop(0)
            co2 = average(co2)
        
def updata_oled():
    t_s = str(temp)
    h_s = str(humid)
    b_s = str(baro)
    c_s = str(co2)
    l_s = str(bright)
    
    oled.fill(0)
    oled.text(t_s, 0, 0, 1)
    oled.text(h_s, 64, 0, 1)
    oled.text(b_s, 0, 16, 1)
    oled.text(c_s, 64, 16, 1)
    oled.text(l_s, 0, 32, 1)
    oled.show()


connect_wifi()
gc.enable()

pin_vent.value(1)

while True:
    time = ticks_ms()
    interval = 1000
    if (ticks_diff(time, passed) > interval):
        for i in range (5):
            update_data()
        updata_oled()
    passed = time
