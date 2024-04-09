"""
ESP32-S3-DevKitC V4/MicroPython
Libraries / Info:
+ bme280 - https://github.com/robert-hh/BME280
+ bh1750 - https://github.com/flrrth/pico-bh1750
+ ccs811 - https://github.com/Notthemarsian/CCS811
+ inmp441 - https://docs.micropython.org/en/latest/library/machine.I2S.html
+ sh1106 - https://github.com/robert-hh/SH1106

Beschreibung: https://nds.edumaps.de/28168/79685/98e7g9w0dw

--- V3: 09.04.2024 ---
--- Jan Krämer, David Grambardt, Riko Pals ---

"""

import gc
from machine import Pin, PWM, SoftI2C, I2S, unique_id, reset
from utime import ticks_ms, ticks_diff, sleep_ms, localtime
import asyncio

import network
from ubinascii import hexlify
from umqtt.simple import MQTTClient
import json
import neopixel

from bme280_float import BME280
from bh1750 import BH1750
import CCS811
import sh1106

# ---------- STATIC VARS ----------
ssid = 'BZTG-IoT'                                           #Schulwlan
password = 'WerderBremen24'
wlan = network.WLAN(network.STA_IF)
MQTT_SERVER = 'broker.hivemq.com'
CLIENT_ID = hexlify(unique_id())
MQTT_TOPIC = 'sensorwerte/*'
loop = asyncio.get_event_loop()

# ---------- DATA ----------
data_b = 420
data_t = 69
data_h = 4200
data_p = 420
data_c = 420
data_n = 69
bright = []
temp = []
humid = []
baro = []
cc = []
dB = []

# ---------- PINS ----------
pin_vent = PWM(Pin(15))
pin_SDA = 9
pin_SCL = 8
sd_pin = Pin(4)
sck_pin = Pin(5)
ws_pin = Pin(6)
n = 12
np = neopixel.NeoPixel(Pin(16), n)

# ---------- I2C + I2S + SENSORS + OLED----------

i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)
i2s = I2S(0,
            sck=sck_pin, ws=ws_pin, sd=sd_pin,
            mode=I2S.RX,
            bits=32,
            format=I2S.MONO,
            rate=16000,
            ibuf=20000)

bh1750 = BH1750(0x23, i2c)
bme280 = BME280(i2c=i2c)
ccs = CCS811.CCS811(i2c, addr=0x5a)
oled = sh1106.SH1106_I2C(128, 64, i2c, Pin(0), 0x3c)
oled.sleep(False)

# ----------- DEFS ----------
def connect_wifi():                                         #fn für WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print(wlan.ifconfig())
    return wlan

def average(values):                                        #fn zum mitteln der Sensorwerte
    if len(values) > 0:                                     #div by 0 umgehen zur Errorvermeidung
        if len(values) > 5:                                 #bei  mehr als 5 Werten den ältesten entfernen um Werte aktuell zu halten
            values.pop(0)
        return sum(values) / len(values)
    else:
        return 1
    
def read_peak():                                            #fn für das Mikrofon
  i2s.init(sck=sck_pin, ws=ws_pin, sd=sd_pin,
            mode=I2S.RX,
            bits=32,
            format=I2S.MONO,
            rate=16000,
            ibuf=20000)
  buffer = bytearray(256)
  i2s.readinto(buffer)
  liste = list(buffer)
  noise = (sum(liste) / len(liste) +1) / 256 * 91 + 30      #prozent(log) zu dB [max = 91dB SNR=61dB min = 30]
  i2s.deinit()
  return noise

def led_reset():                                            #fn zum initialem zurücksetzen der ws2812's
    for i in range (n):
        np[i] = (0, 0, 0)
        np.write()
              
# ----------- LOOPS ----------

async def np():                                             #schleife zum aktualisieren der ws2812's anhand der Limit-Werte aus der Edumap
    global temp, humid, cc, dB
    passed = 0
    interval = 1000
    while True:
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):
            if temp >= 20 and temp <= 23:
                np[0] = (0, 255, 0)
                np[1] = (0, 255, 0)
                np[2] = (0, 255, 0)
            
            if temp >= 18 and temp < 20 or temp >23 and temp <= 25:
                np[0] = (255, 255, 0)
                np[1] = (255, 255, 0)
                np[2] = (255, 255, 0)
            
            if temp < 18 or temp > 25:
                np[0] = (255, 0, 0)
                np[1] = (255, 0, 0)
                np[2] = (255, 0, 0)
            
            
            if humid >= 40 and humid <= 60:
                np[3] = (0, 255, 0)
                np[4] = (0, 255, 0)
                np[5] = (0, 255, 0)
            
            if humid >= 30 and humid < 40 or humid > 60 and humid <= 70:
                np[3] = (255, 255, 0)
                np[4] = (255, 255, 0)
                np[5] = (255, 255, 0)
            
            if humid < 30 or humid > 70:
                np[3] = (255, 0, 0)
                np[4] = (255, 0, 0)
                np[5] = (255, 0, 0)
            
            
            if cc <= 1000:
                np[6] = (0, 255, 0)
                np[7] = (0, 255, 0)
                np[8] = (0, 255, 0)
            
            if cc > 1000 and cc < 2000:
                np[6] = (255, 255, 0)
                np[7] = (255, 255, 0)
                np[8] = (255, 255, 0)
            
            if cc > 2000:
                np[6] = (255, 0, 0)
                np[7] = (255, 0, 0)
                np[8] = (255, 0, 0)
            
            
            if dB <= 50:
                np[9] = (0, 255, 0)
                np[10] = (0, 255, 0)
                np[11] = (0, 255, 0)
            
            if dB >50 and dB < 65:
                np[9] = (255, 255, 0)
                np[10] = (255, 255, 0)
                np[11] = (255, 255, 0)
            
            if dB >65:
                np[9] = (255, 0, 0)
                np[10] = (255, 0, 0)
                np[11] = (255, 0, 0)
            
            np.write()
            gc.collect()
            passed = time
        await asyncio.sleep_ms(10)

async def oled_w():                                         #schleife zum aktualisieren des Displays
    global data_b, data_t, data_h, data_p, data_c, data_n
    namen = ['Helligkeit:', 'Temperatur:', 'Feuchtigkeit:', 'Atmos. Druck:', 'Co2 Anteil:', 'Lautstaerke:']
    werte = [str(int(data_b))  + ' Lux', str(round(data_t,1)) + ' C', str(round(data_h,1)) + ' %', str(int(data_p)) + ' hPa', str(int(data_c)) + ' ppm', str(int(data_n)) + ' dBA']
    passed = 0
    interval = 3000
    index_list = 0
    while True:
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):
            name = namen[index_list]
            wert = werte[index_list]
            oled.fill(0)
            oled.text(name, 8, 12, 1)
            oled.text(wert, 8, 36, 1)
            oled.show()
            index_list += 1
            if index_list >= len(werte):
                index_list = 0
            gc.collect()
            passed = time
        await asyncio.sleep_ms(1)
        
async def sensors_read():                                   #schleife zum auslesen aller Sensoren
    global bright, temp, humid, baro, cc, dB, data_b, data_t, data_h, data_p, data_c, data_n
    passed = 0
    interval = 1000
    while True:
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):                           #interval von 1er sekunde
            try:                                                            #errorvermeidung bei i2c problemen
                b = int(bh1750.measurement)
                bright.append(b)
                data_b = average(bright)                                    #werte werden direkt nach abfrage gemittelt, Liste könnte sonst unkontrollierbar lang werden
            except:
                print("konnte Helligkeit nicht auslesen")
            try:
                t = int(bme280.value_t)
                temp.append(t)                                              #eventuell ist ein rausrechnen der Erwärmung über gnd pin vom ESP chip
                data_t = average(temp)
            except:
                print("konnte Temperatur nicht auslesen")
            try:                
                h = int(bme280.value_h)
                humid.append(h)
                data_h = average(humid)
            except:
                print("konnte Feuchtigkeit nicht auslesen")
            try:                
                p = int(bme280.value_p * 0.01)
                baro.append(p)
                data_p = average(baro)
            except:
                print("konnte atmos. Druck nicht auslesen")
            try:            
                if ccs.data_ready():
                    c = (ccs.eCO2)
                    if c != 0:
                        cc.append(c)
                        data_c = average(cc)
            except:
                print("konnte Co2 Gehalt nicht auslesen")
            try:            
                noise = read_peak()
                dB.append(noise)
                data_n = average(dB)
            except:
                print("konnte Lautstärke nicht auslesen")
                            
            gc.collect()                                            #ram säubern
            passed = time
        await asyncio.sleep_ms(10)

async def mqtt_send():                                              #schleife zum senden der Daten 
    global CLIENT_ID, MQTT_SERVER, MQTT_TOPIC
    passed = 0
    interval = 5000
    client = MQTTClient(CLIENT_ID, MQTT_SERVER)
    while True:
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):                   #schleife wird alle 5 Sekunden durchlaufen
            client.connect()
            werte = {
                'Bright': round(data_b,0),
                'Temp': round(data_t,1),
                'Humid': round(data_h,1),
                'Baro': round(data_p,0),
                'Carbon': round(data_c,0),
                'Noise': round(data_n,0),
                }
            dump = json.dumps(werte)                                #json formatieren und versenden
            client.publish(MQTT_TOPIC, dump)
            print(dump)
            client.disconnect()
            gc.collect()
            passed = time
        await asyncio.sleep_ms(10)

connect_wifi()

pin_vent.freq(1000)
pin_vent.duty(1023)                                                 #anstellen des Lüftern

led_reset()

loop.close()

try:
    loop.create_task(sensors_read())
    loop.create_task(mqtt_send())
    loop.create_task(oled_w())
    loop.create_tast(np())
    loop.run_forever()
except Exception as e:
    print("Error:", e)
finally:
    loop.close()
    print("manual reset")


