import machine
import random

def text_to_pages(text):
    words = text.split()
    pages = []
    current_page = words[0]
    for word in words[1:]:
        if len(current_page) + len(word) + 1 <= 21:
            current_page += " " + word
        else:
            pages.append(current_page)
            current_page = word
    pages.append(current_page)
    return pages

def page_to_bytes(page, cmap):
    bytes = bytearray(128)
    index = 1
    for char in page:
        bytes[index:index + 6] = cmap[char]
        index += 6
    return bytes

class Chatzkel:
    def __init__(self, display, rotary, quotes, cmap):
        self.display = display
        self.rotary = rotary
        self.rotary.set_irq_turn(self.knob_turn)
        self.rotary.set_irq_push(self.knob_push)
        self.quotes = quotes
        self.cmap = cmap
        self.quote = None
        self.quote_bytes = []
        self.display_bytes = 0
        self.display_buffer = bytearray()
        self.timer = machine.Timer(-1)
        self.update()

    def update_wrapper(self, timer):
        self.update()
    
    def update(self):
        self.fetch_quote()
        self.refresh_quote_bytes()
        self.display_bytes = 0
        self.refresh_display()
        self.set_timer()
    
    def set_timer(self):
        random_interval = random.randint(3000000, 30000000)
        self.timer.init(period=random_interval, mode=machine.Timer.ONE_SHOT, callback=self.update_wrapper)

    def fetch_quote(self):
        self.quote = None
        self.quote = random.choice(self.quotes)
        
    def refresh_quote_bytes(self):
        self.quote_bytes = []
        self.quote_bytes = [page_to_bytes(page, self.cmap) for page in text_to_pages(self.quote)]
        while len(self.quote_bytes) < 8:
            self.quote_bytes.append(bytearray(b'\x00' * 128))

    def refresh_display(self):
        self.display_buffer = bytearray()
        start_index = self.display_bytes
        end_index = start_index + 8
        end_index = min(end_index, len(self.quote_bytes))
        for i in range(start_index, end_index):
            self.display_buffer += self.quote_bytes[i]
        self.display.i2c.writevto(self.display.addr, (b"\x40", self.display_buffer))
    
    def knob_turn(self, direction):
        self.display_bytes += direction
        if self.display_bytes < 0:
            self.display_bytes = 0
        if self.display_bytes + 8 > len(self.quote_bytes):
            self.display_bytes = len(self.quote_bytes) - 8
        self.refresh_display()
    
    def knob_push(self):
        self.update()