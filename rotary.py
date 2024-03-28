# Based on 	https://github.com/miketeachman/micropython-rotary/blob/master/rotary_irq_rp2.py

from machine import Pin
from micropython import const
from time import sleep
import time

_DIR_NONE = const(0x00)
_DIR_CW = const(0x10)
_DIR_CCW = const(0x20)
_R_START = const(0x0)

_transition_table = [
    [0x3, 0x2, 0x1, 0x0], [0x23, 0x0, 0x1, 0x0], [0x13, 0x2, 0x0, 0x0], [0x3, 0x2, 0x1, 0x0],
    [0x3, 0x0, 0x1, 0x10], [0x3, 0x2, 0x0, 0x0], [0x3, 0x0, 0x1, 0x0], [0x3, 0x2, 0x1, 0x20],
    [0x3, 0x2, 0x1, 0x0], [0x3, 0x0, 0x0, 0x0], [0x3, 0x2, 0x0, 0x0], [0x3, 0x0, 0x1, 0x0],
    [0x3, 0x0, 0x1, 0x0], [0x3, 0x2, 0x0, 0x0], [0x3, 0x0, 0x0, 0x0], [0x3, 0x2, 0x1, 0x0],
]

_STATE_MASK = const(0x03)
_DIR_MASK = const(0x30)

class RotaryEncoder(object):
    def __init__(self, pin_clk, pin_dt, pin_sw):
        self._state = _R_START
        self._dir = _DIR_NONE
        self._pin_clk = Pin(pin_clk, Pin.IN, Pin.PULL_UP)
        self._pin_dt = Pin(pin_dt, Pin.IN, Pin.PULL_UP)
        self._pin_sw = Pin(pin_sw, Pin.IN, Pin.PULL_UP)
        self.irq_turn = None
        self.irq_push = None
        self._last_push_time = 0
        self._debounce_ms = 100
        self._enable_irq()
    
    def _enable_irq(self):
        self._pin_clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._process_turn)
        self._pin_dt.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._process_turn)
        self._pin_sw.irq(trigger=Pin.IRQ_FALLING, handler=self._process_push)

    def _process_turn(self, pin):
        clk_val = self._pin_clk.value()
        dt_val = self._pin_dt.value()
        current_state = clk_val | (dt_val << 1)
        self._state = _transition_table[self._state & _STATE_MASK][current_state]
        direction = self._state & _DIR_MASK
        if direction == _DIR_CW:
            self.irq_turn(1)
        elif direction == _DIR_CCW:
            self.irq_turn(-1)
        self._state &= ~_DIR_MASK
        
    def _process_push(self, pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self._last_push_time) > self._debounce_ms:
            self.irq_push()
            print("irq")
            self._last_push_time = current_time

    def set_irq_turn(self, parent_turn_funct):
        self.irq_turn = parent_turn_funct
        
    def set_irq_push(self, parent_push_funct):
        self.irq_push = parent_push_funct
        print("parent")

    def close(self):
        self._pin_clk.irq(handler=None)
        self._pin_dt.irq(handler=None)
        self._pin_sw.irq(handler=None)
