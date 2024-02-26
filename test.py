from machine import Pin, SoftI2C
import machine
from time import sleep_ms
import utime
from bme280_float import BME280
from bh1750 import BH1750
import CCS811
import sh1106

pin_SDA = 9
pin_SCL = 8

pin_air = Pin(15, Pin.OUT)

bright = []
temp = []
humid = []
baro = []
cc = []
db = []

i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)

bh1750 = BH1750(0x23, i2c)
bme280 = BME280(i2c=i2c)
ccs = CCS811.CCS811(i2c, addr=0x5a)

oled = sh1106.SH1106_I2C(128, 64, i2c, Pin(0), 0x3c)
oled.sleep(False)

while True:
    bright = str(bh1750.measurement)
    temp = str(bme280.value_t)
    humid = str(bme280.value_h)
    baro = str(bme280.value_p)
    if ccs.data_ready():
        cc = str('%d ppm' % (ccs.eCO2))
    sleep_ms(1000)
    oled.fill(0)
    oled.text(bright, 4, 0, 1)
    oled.text(temp, 4, 10, 1)
    oled.text(humid, 4, 20, 1)
    oled.text(baro, 4, 30, 1)
    oled.text(cc, 4, 40, 1)
    oled.show()
