# Write your code here :-)
import board
from digitalio import DigitalInOut, Direction

import time
import terminalio
from adafruit_magtag.magtag import MagTag

magtag = MagTag()
magtag.add_text(
    text_font = terminalio.FONT,
    text_position = (50, (magtag.graphics.display.height // 2) - 1),
    text_scale = 3,
)

magtag.set_text("Hello Helen")

button_colors = ((23, 161, 235))
#button_colors = ((255, 0, 0), (255, 150, 0), (0, 255, 255), (180, 0, 255))
while True:
    magtag.peripherals.neopixel_disable = False
    magtag.peripherals.neopixels.fill(button_colors[0])
    time.sleep(1)

###### Not working pixels

# import neopixel
# pixels = neopixel.NeoPixel(board.NEOPIXEL, 4, brightness=0.4, pixel_order=neopixel.RGB, auto_write=False)
# pixels[0] = (255, 0, 0)
# pixels[1] = (10, 10, 0)
# pixels[2] = (10, 0, 10)
# pixels[3] = (10, 10, 10)
# pixels.show()
# print('lit')


###### Music playing

#import adafruit_rtttl

#spkrenable = DigitalInOut(board.SPEAKER_ENABLE)
#spkrenable.direction = Direction.OUTPUT
#spkrenable.value = True

#adafruit_rtttl.play(board.SPEAKER, "Snowman:d=8,o=5,b=200:2g,4e.,f,4g,2c6,b,c6,4d6,4c6,4b,a,2g.,b,c6,4d6,4c6,4b,a,a,g,4c6,4e.,g,a,4g,4f,4e,4d,2c.,4c,4a,4a,4c6,4c6,4b,4a,4g,4e,4f,4a,4g,4f,2e.,4e,4d,4d,4g,4g,4b,4b,4d6,d6,b,4d6,4c6,4b,4a,4g,4p,2g")
#adafruit_rtttl.play(board.SPEAKER, "Snowman:d=8,o=5,b=200:c,c,d,c,d,e,d,c,d,e,f,e,d,c,d,e,f,g,f,e,d,c,c")



###### Blinky RED Light

#led = digitalio.DigitalInOut(board.D13)
#led.direction = digitalio.Direction.OUTPUT

#while True:
#    led.value = True
#    time.sleep(0.1)
#    led.value = False
#    time.sleep(0.5)
