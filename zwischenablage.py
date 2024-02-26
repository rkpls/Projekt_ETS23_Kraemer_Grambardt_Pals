from time import sleep_ms
from machine import Pin, SoftI2C, SoftSPI
from dht import DHT11
from bme280_float import BME280
import CCS811
from mq135 import MQ135
import sh1106

pin_bme_sda = 12
pin_bme_scl = 13
pin_ccs_sda = 27
pin_ccs_scl = 14

mq135 = MQ135(35)
dht11 = DHT11(Pin(34))

pin_sck = 18
pin_mosi = 23
pin_miso = 22
pin_res = 4
pin_dc = 15
pin_cs = 2

spi = SoftSPI(sck=Pin(pin_sck), mosi=Pin(pin_mosi), miso=Pin(pin_miso), baudrate=4000000)
oled = sh1106.SH1106_SPI(128, 64, spi, Pin(pin_dc), Pin(pin_res), Pin(pin_cs))

pin_air = Pin(25, Pin.OUT)
pin_rpm = Pin(26, Pin.IN)

i2c_bme = SoftI2C(scl=Pin(pin_bme_scl), sda=Pin(pin_bme_sda), freq=1000000)
i2c_ccs = SoftI2C(scl=Pin(pin_ccs_scl), sda=Pin(pin_ccs_sda), freq=1000000)

pin_air.value(1)
pin_air.on()

bme280 = BME280(i2c=i2c_bme)
s = CCS811.CCS811(i2c=i2c_ccs)

temp = 0
humid = 0
baro = 0
quality = 0

print("Start")
oled.sleep(False)
pin_air.on()
while True:
    try:
        temp = (bme280.value_t)
    except:
        temp = "ERR"
    try:
        humid = (bme280.value_h)    
    except:
        humid = "ERR"
    try:    
        baro = (bme280.value_p)
    except:
        baro = "ERR"
    try:
        if s.data_ready():
            carbon = s.eCO2
    except:
        carbon = "ERR"
    try:
        dht11.measure()
        temperature = dht11.temperature()
        humidity = dht11.humidity()

        rzero = mq135.get_rzero()
        corrected_rzero = mq135.get_corrected_rzero(temperature, humidity)
        resistance = mq135.get_resistance()
        ppm = mq135.get_ppm()
        corrected_ppm = mq135.get_corrected_ppm(temperature, humidity)

        print("DHT11 Temperature: " + str(temperature) +"\t Humidity: "+ str(humidity))
        print("MQ135 RZero: " + str(rzero) +"\t Corrected RZero: "+ str(corrected_rzero)+
              "\t Resistance: "+ str(resistance) +"\t PPM: "+str(ppm)+
              "\t Corrected PPM: "+str(corrected_ppm)+"ppm")
    except:
        print("ERR")
    
    t_s = str(temp)
    h_s = str(humid)
    b_s = str(baro)
    c_s = str(carbon)
    q_s = str(quality)
    
    oled.fill(0)
    oled.text(t_s, 0, 0, 1)
    oled.text(h_s, 64, 0, 1)
    oled.text(b_s, 0, 16, 1)
    oled.text(c_s, 64, 16, 1)
    oled.text(b_s, 0, 32, 1)
    oled.text("-", 64, 32, 1)
    oled.text("-", 0, 48, 1)
    oled.text("-", 64, 48, 1)
    oled.show()
    sleep_ms(1000)
    
    

