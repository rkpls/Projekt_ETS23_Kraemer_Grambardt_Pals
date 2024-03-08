from machine import I2S, Pin

# GPIO-Pins für den INMP441
sd_pin = Pin(6, Pin.IN)
sck_pin = Pin(5, Pin.IN)
ws_pin = Pin(4, Pin.IN)

# I2S-Konfiguration
i2s = I2S(2,
          sck=sck_pin,
          ws=ws_pin,
          sd=sd_pin,
          mode=I2S.RX,
          bits=16,
          format=I2S.MONO,
               rate=22050,
               ibuf=20000)

# Funktion zum Lesen eines Peaks
def read_peak():
  # Starten der I2S-Übertragung
  i2s.start()

  # Puffer zum Speichern der Audiodaten
  buffer = bytearray(256)

  # Lesen von 256 Audiodaten
  i2s.readinto(buffer)

  # Berechnen des Peak-Werts
  peak = max(buffer)

  # Stoppen der I2S-Übertragung
  i2s.stop()

  return peak

# Endlosschleife zum Lesen von Peaks
while True:
  peak = read_peak()
  print(peak)