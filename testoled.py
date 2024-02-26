
from machine import Pin, SoftI2C
import machine
from time import sleep_ms
import utime
import sh1106

pin_SDA = 9
pin_SCL = 8


i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)
oled = sh1106.SH1106_I2C(128, 64, i2c, Pin(0), 0x3c)
oled.sleep(False)

def scan_i2c():
    print('Scan i2c')
    devices = i2c.scan()

    for device in devices:  
        print("Hex address: ",hex(device))
    if len(devices) == 0:
        print("No i2c device !")
    else:
        print('i2c devices found:',len(devices))
        
scan_i2c()

oled.fill(0)
oled.text('Display Test', 0, 0, 1)
oled.hline(0, 9, 127, 1)
oled.hline(0, 30, 127, 1)
oled.vline(0, 10, 32, 1)
oled.vline(127, 10, 32, 1)

for i in range(0, 118):
    oled.fill_rect(i,10, 10, 10, 1)
    oled.fill_rect(10, 21, 30, 8, 0)
    oled.text(str(i), 10, 21, 1)
    oled.show()

