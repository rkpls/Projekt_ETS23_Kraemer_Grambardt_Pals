from machine import Pin, SoftI2C
import machine
from time import sleep_ms
import utime
from bh1750 import BH1750

pin_SDA = 9
pin_SCL = 8

bright = 0

i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)

bh1750 = BH1750(0x23, i2c)

while True:
    print(bh1750.measurement)
    sleep_ms(1000)
