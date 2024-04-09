from machine import I2S, Pin
from time import sleep_ms
import ustruct

# GPIO-Pins für den INMP441
sd_pin = Pin(4)
sck_pin = Pin(5)
ws_pin = Pin(6)

# I2S-Konfiguration
i2s = I2S(0,
            sck=sck_pin, ws=ws_pin, sd=sd_pin,
            mode=I2S.RX,
            bits=16,
            format=I2S.MONO,
            rate=16000,
            ibuf=20000)


def read_peak():
  i2s.init(sck=sck_pin, ws=ws_pin, sd=sd_pin,
            mode=I2S.RX,
            bits=16,
            format=I2S.MONO,
            rate=16000,
            ibuf=20000)
  buffer = bytearray(256)
  i2s.readinto(buffer)
  liste = list(buffer)
  noise = sum(liste) / len(liste)
  i2s.deinit()
  return noise


while True:
  peak = read_peak()
  print(peak)
  sleep_ms(1000)