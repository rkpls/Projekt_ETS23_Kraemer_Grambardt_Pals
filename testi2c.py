
from machine import Pin, SoftI2C

pin_SDA = 9
pin_SCL = 8


i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)

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