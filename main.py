"""
ESP32-S3-DevKitC V4/MicroPython
Libraries / Info:
+ bme280 - https://github.com/robert-hh/BME280
+ bh1750 - https://github.com/flrrth/pico-bh1750
+ ccs811 - https://github.com/Notthemarsian/CCS811
+ inmp441 - https://docs.micropython.org/en/latest/library/machine.I2S.html
+ sh1106 - https://github.com/robert-hh/SH1106

Beschreibung: https://nds.edumaps.de/28168/79685/98e7g9w0dw

--- V4: 15.04.2024 ---
--- Jan Krämer, David Grambardt, Riko Pals ---
"""

import gc
from machine import Pin, PWM, SoftI2C, I2S, unique_id, reset
from utime import ticks_ms, ticks_diff, sleep_ms
import asyncio

import network
from ubinascii import hexlify                                           #verwendet für mqqt geräte ID mit unique_id
from umqtt.simple import MQTTClient
import json
import neopixel

from bme280_float import BME280
from bh1750 import BH1750
import CCS811
import sh1106

# ---------- STATIC VARS ----------
ssid = '***'                                                       #Schulwlan
password = '***'
wlan = network.WLAN(network.STA_IF)
MQTT_SERVER = 'broker.hivemq.com'
CLIENT_ID = hexlify(unique_id())                                        #client id für mqtt
MQTT_TOPIC = 'sensorwerte/*'                                            #mqtt topic
loop = asyncio.get_event_loop()

# ---------- DATA ----------
data_b = 0                                                              #globale variablen standardwerte werden festgelegt zur vermeidung von 0-Wert-Ausgabe
data_t = 20
data_h = 50
data_p = 10000
data_c = 400
data_n = 30
bright = []                                                             #Listen, verwendet zum mitteln der Werte
temp = []
humid = []
baro = []
cc = []
dB = []

# ---------- PINS ----------
pin_vent = PWM(Pin(15))                                                 #pwm Pin für Lüfter
pin_SDA = 9
pin_SCL = 8
sd_pin = Pin(5)
sck_pin = Pin(4)
ws_pin = Pin(6)
np = neopixel.NeoPixel(Pin(16), 12)                                     #1 draht Bus für wled/neopixel protokoll

# ---------- I2C + I2S + SENSORS + OLED----------
i2c = SoftI2C(scl=Pin(pin_SCL), sda=Pin(pin_SDA), freq=100000)          #2 draht i2c Bus für Olded, bh1750, bme280, ccs
i2s = I2S(0,                                                            #3 draht i2s Bus für Mikrofon 
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
def connect_wifi():                                                         #fn für WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print(wlan.ifconfig())
    return wlan

def average(values):                                                        #fn zum mitteln der Sensorwerte
    if len(values) > 0:                                                 #div by 0 umgehen zur Errorvermeidung
        if len(values) > 10:                                            #bei  mehr als 5 Werten den ältesten entfernen um Werte aktuell zu halten
            values.pop(0)
        return sum(values) / len(values)
    else:
        return 1
    
def read_peak():                                                            #fn für das Mikrofon (aus Bilbliothek)
  i2s.init(sck=sck_pin, ws=ws_pin, sd=sd_pin,
            mode=I2S.RX,
            bits=32,
            format=I2S.MONO,
            rate=16000,
            ibuf=20000)
  buffer = bytearray(256)
  i2s.readinto(buffer)
  liste = list(buffer)
  noise = (sum(liste) / len(liste) +1) / 256 * 91 + 30                      #prozent (logarithmisch) zu dBA [max = 91dB SNR=61dB min = 30]
  i2s.deinit()
  return noise

def led_reset():                                                            #fn zum initialem zurücksetzen der ws2812's
    np[0] = (0, 0, 0)
    np[1] = (0, 0, 0)
    np[2] = (0, 0, 0)
    np[3] = (0, 0, 0)
    np[4] = (0, 0, 0)
    np[5] = (0, 0, 0)
    np[6] = (0, 0, 0)
    np[7] = (0, 0, 0)
    np[8] = (0, 0, 0)
    np[9] = (0, 0, 0)
    np[10] = (0, 0, 0)
    np[11] = (0, 0, 0)
    np.write()
              
# ---------- THREAD DEF ----------

async def led():                                                            #schleife zum aktualisieren der ws2812's anhand der Limit-Werte aus der Edumap
    global data_t, data_h, data_c, data_n
    passed = 0
    interval = 500
    while True:
        temp = data_t
        humid = data_h
        cc = data_c
        dB = data_n
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

async def oled_w():                                                         #schleife zum aktualisieren des Displays
    global data_b, data_t, data_h, data_p, data_c, data_n
    passed = 0
    interval = 3000
    index_list = 0
    while True:
        namen = ['Helligkeit:', 'Temperatur:', 'Feuchtigkeit:', 'Atmos. Druck:', 'Co2 Anteil:', 'Lautstaerke:']
        werte = [str(int(data_b))  + ' Lux', str(int(data_t)) + ' C', str(int(data_h)) + ' %', str(int(data_p)) + ' hPa', str(int(data_c)) + ' ppm', str(int(data_n)) + ' dBA']                  #aktualsieren der indexierten liste mit aktuellen Daten
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):
            name = namen[index_list]
            wert = werte[index_list]
            oled.fill(0)
            oled.text(name, 8, 12, 1)
            oled.text(wert, 8, 36, 1)
            oled.show()
            index_list += 1									                #erhöhung des Index für die nächste Anzeige
            if index_list >= len(werte):
                index_list = 0								                #reset wenn alle durchgelaufen sind
            gc.collect()
            passed = time
        await asyncio.sleep_ms(1)
        
async def sensors_read():                                                   #schleife zum auslesen aller Sensoren
    global bright, temp, humid, baro, cc, dB, data_b, data_t, data_h, data_p, data_c, data_n
    passed = 0
    interval = 100
    while True:
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):                       #interval von 1er sekunde                                                        
            b = int(bh1750.measurement)
            bright.append(b)
            data_b = average(bright)                                    #werte werden direkt nach abfrage gemittelt, Liste könnte sonst unkontrollierbar lang werden           		
            t = int(bme280.value_t)									    #lesen mitteln und schreiben von bme temperatur
            temp.append(t)                                              
            data_t = average(temp) -5           						#eventuell ist ein rausrechnen der Erwärmung über gnd pin vom ESP chip					               
            h = int(bme280.value_h)                                     #lesen mitteln und schreiben von bme feuchtigkeit 
            humid.append(h)
            data_h = average(humid)           											
            p = int(bme280.value_p * 0.01)                              #lesen mitteln und schreiben von bme druck
            baro.append(p)
            data_p = average(baro)     											
            if ccs.data_ready():                                        #lesen mitteln und schreiben von ccs co2 anteil
                c = (ccs.eCO2)
                if c != 0:
                    cc.append(c)
                    data_c = average(cc)
            noise = read_peak()                                         #lesen mitteln und schreiben des microfon Lautstärkewertes (aufruf funktion Z102)
            data_n = noise                  
            gc.collect()                                            	#ram säubern
            passed = time
        await asyncio.sleep_ms(10)

async def mqtt_send():                                              	    #schleife zum senden der Daten 
    global CLIENT_ID, MQTT_SERVER, MQTT_TOPIC
    passed = 0
    interval = 5000
    client = MQTTClient(CLIENT_ID, MQTT_SERVER)
    while True:
        time = ticks_ms()
        if (ticks_diff(time, passed) > interval):                   		#schleife wird alle 5 Sekunden durchlaufen
            client.connect()
            werte = {
                'Bright': int(data_b),
                'Temp': int(data_t),
                'Humid': int(data_h),
                'Baro': int(data_p),
                'Carbon': int(data_c),
                'Noise': int(data_n),
                }
            dump = json.dumps(werte)                                		#json formatieren und versenden
            client.publish(MQTT_TOPIC, dump)
            print(dump)
            client.disconnect()
            gc.collect()
            passed = time
        await asyncio.sleep_ms(10)

# ---------- STARTUP ----------
connect_wifi()
pin_vent.freq(1000)
pin_vent.duty(1023)                                                         #anstellen des Lüftern
led_reset()

# ---------- LOOP ----------
try:                                                                        #aufsetzen der parallel laufenden Funktionen
    loop.create_task(sensors_read())
    loop.create_task(mqtt_send())
    loop.create_task(oled_w())
    loop.create_task(led())
    loop.run_forever()
except Exception as e:
    print("Error:", e)
finally:
    loop.close()
    print("automatic reset in 5s")
    sleep_ms(5000)
    reset()                                                                 #bei error autom. neustart nach 5 sek
    
