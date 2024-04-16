import neopixel
from machine import Pin

led_ring = neopixel.NeoPixel(Pin(16), 12)

led_ring[0] = (0, 255, 0)
led_ring[1] = (0, 255, 0)
led_ring[2] = (0, 255, 0)
led_ring[3] = (255, 0, 0)
led_ring[4] = (255, 0, 0)
led_ring[5] = (255, 0, 0)
led_ring[6] = (0, 0, 255)
led_ring[7] = (0, 0, 255)
led_ring[8] = (0, 0, 255)
led_ring[9] = (127, 127, 0)
led_ring[10] = (127, 127, 0)
led_ring[11] = (127, 127, 0)

led_ring.write()
