import machine
import neopixel
import time

NUM_PIXELS = 12
PIN_NUM = 15

np = neopixel.NeoPixel(machine.Pin(PIN_NUM), NUM_PIXELS)

def set_all_pixels(r, g, b):
    for i in range(NUM_PIXELS):
        np[i] = (r, g, b)
    np.write()

def clear_all_pixels():
    set_all_pixels(0, 0, 0)

def test_neopixels():
    print("Testing NeoPixels...")
    while True:
        # Set all pixels to red
        set_all_pixels(255, 0, 0)
        time.sleep(1)
        # Set all pixels to green
        set_all_pixels(0, 255, 0)
        time.sleep(1)
        # Set all pixels to blue
        set_all_pixels(0, 0, 255)
        time.sleep(1)
        # Clear all pixels
        clear_all_pixels()
        time.sleep(1)

test_neopixels()
