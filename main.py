from SSD1306 import SSD1306_I2C
from machine import Pin, I2C
from string_list import my_list
from dict import character_map
from rotary import RotaryEncoder
from chatzkel import Chatzkel



DISPLAY_SDA_PIN = 18 
DISPLAY_SCL_PIN = 19
ROTARY_CLK_PIN = 21
ROTARY_DT_PIN = 20
ROTARY_SW_PIN = 22



i2c = I2C(1, sda=Pin(DISPLAY_SDA_PIN), scl=Pin(DISPLAY_SCL_PIN))
display = SSD1306_I2C(128, 64, i2c)
rotary = RotaryEncoder(pin_clk=ROTARY_CLK_PIN, pin_dt=ROTARY_DT_PIN, pin_sw=ROTARY_SW_PIN)



chatzkel = Chatzkel(display, rotary, my_list, character_map)