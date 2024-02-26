from machine import Pin, SoftI2C
import machine
from time import sleep_ms
import utime
from bme280_float import BME280
from bh1750 import BH1750
import CCS811

pin_SDA = 9
pin_SCL = 8

bright = 0

i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)

bh1750 = BH1750(0x23, i2c)
bme280 = BME280(i2c=i2c)
ccs = CCS811.CCS811(i2c, addr=0x5a)


while True:
    print(bh1750.measurement)
    print(bme280.value_t)
    print(bme280.value_h)
    print(bme280.value_p)
    if ccs.data_ready():
        print('eCO2: %d ppm, TVOC: %d ppb' % (ccs.eCO2, ccs.tVOC))
    sleep_ms(1000)