from machine import Pin
import neopixel

# Define the number of LEDs and the pin they're connected to
num_leds = 12  # Change this to match the number of LEDs in your strip
pin_led = 16     # Change this to match the GPIO pin you've connected the strip to

# Initialize the Neopixel strip
np = neopixel.NeoPixel(Pin(pin_led), num_leds)

# Function to set all LEDs to a specific color
def set_all_leds(r, g, b):
    for i in range(num_leds):
        np[i] = (r, g, b)
    np.write()

# Set all LEDs to red
set_all_leds(255, 0, 0)
