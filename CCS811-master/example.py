from time import sleep_ms
from machine import SoftI2C, Pin
from bme280_float import BME280
import CCS811

i2c_ccs = SoftI2C(sda=Pin(9), scl=Pin(8))
s = CCS811.CCS811(i2c_ccs, addr=0x5a)
while True:
    if s.data_ready():
        print('eCO2: %d ppm, TVOC: %d ppb' % (s.eCO2, s.tVOC))
        sleep_ms(1000)