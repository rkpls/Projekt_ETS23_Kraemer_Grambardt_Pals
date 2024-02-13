#
# Example. Using I2C at P9, P10
#
from machine import SoftI2C, Pin
from bme280_float import *
from utime import sleep

pin_bme_sda = 23
pin_bme_scl = 22
i2c_bme = SoftI2C(scl=Pin(pin_bme_scl), sda=Pin(pin_bme_sda), freq=100000)
bme280 = BME280(i2c=i2c_bme)
while True:
    print(bme280.values)
    sleep(1)

