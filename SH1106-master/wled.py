import machine, neopixel

num = 12
pin = machine.Pin(16)
pixel = neopixel.NeoPixel(pin,num)

for i in range(30,1,1):
    pixel[i] = (255,0,0)
    pixel[i+1] = (0,255,0)
    pixel[i+2] = (0,0,255)
    pixel.write()