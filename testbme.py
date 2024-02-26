from machine import Pin, SoftI2C
import machine
from time import sleep_ms
import utime
from bme280_float import BME280


pin_SDA = 9
pin_SCL = 8

values = 0

i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)

bme280 = BME280(i2c=i2c)

while True:
    print(bme280.value_t)
    print(bme280.value_h)
    print(bme280.value_p)
    sleep_ms(1000)