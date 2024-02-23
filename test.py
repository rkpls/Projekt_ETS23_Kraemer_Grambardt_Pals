import gc
import network
from machine import Pin, SoftI2C
from utime import ticks_ms, ticks_diff

from bme280_float import *
from CCS811 import CCS811
from bh1750 import BH1750

pin_scl = Pin(8)
pin_sda = Pin(9)
i2s_data_pin = 4
i2s_clk_pin = 5
i2s_ws_pin = 6
pin_vent = Pin(16, Pin.OUT)

i2c = SoftI2C(scl=pin_scl, sda=pin_sda, freq=1000000)

bme280 = BME280(i2c=i2c)
bh1750 = BH1750(0x23, i2c)

temp = []
humid = []
baro = []
bright =[]
co2 = []

passed = 0

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

gc.enable()
pin_vent.value(1)

print(bme280.values)
print(bh1750.measurement)

while True:
    time = ticks_ms()
    interval = 1000
    if (ticks_diff(time, passed) > interval):
        for i in range(5):
            update_data()
    passed = time
    
    