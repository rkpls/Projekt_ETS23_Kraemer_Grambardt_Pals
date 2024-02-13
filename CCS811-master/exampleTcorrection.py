"""Example usage basic driver CCS811.py"""

from machine import Pin, SoftI2C
import time
import CCS811
import bme280_float as BME280
import sh1106


def main():
    i2c = SoftI2C(scl=Pin(13), sda=Pin(12))
    s = CCS811.CCS811(i2c)
    b = BME280.BME280(i2c=i2c)
    time.sleep(1)
    while True:
        if s.data_ready():
            print('eCO2: %d ppm, TVOC: %d ppb' % (s.eCO2, s.tVOC), b.values)
            r = b.read_compensated_data()
            t = r[0]/100
            p = r[1]/25600
            h = r[2]/1024
            x,y = s.get_baseline()
            s.put_envdata(humidity=h,temp=t)
            time.sleep(1)

main()
