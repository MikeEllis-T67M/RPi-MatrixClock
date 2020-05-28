from gps3 import gps3
from gps3.agps3threaded import AGPS3mechanism

import RPi.GPIO as GPIO

from time import sleep, strftime
from datetime import datetime

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT

from clock_font import CLOCK_FONT

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8, block_orientation=-90)
device.contrast(5)
virtual = viewport(device, width=32, height=16)
show_message(device, 'GPS Clock', fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)

def satellites_used(feed):
    """Counts number of satellites used in calculation from total visible satellites
    Arguments:
        feed feed=data_stream.TPV['satellites']
    Returns:
        total_satellites(int):
        used_satellites (int):
    """
    total_satellites = 0
    used_satellites = 0

    if not isinstance(feed, list):
        return 0, 0

    for satellites in feed:
        total_satellites += 1
        if satellites['used'] is True:
            used_satellites += 1
    return total_satellites, used_satellites
    
try:
    # Process the raw GPS info in a background thread
    gps3_thread = AGPS3mechanism()
    gps3_thread.stream_data()
    gps3_thread.run_thread()
    
    while True:
        curtime = datetime.now().second
        now = datetime.now().strftime('%H:%M')
        
        if curtime == 10:
            with canvas(virtual) as draw:
                show_message(device, "GPS: Using " + str(satellites_used(gps3_thread.data_stream.satellites)[1]) + " of " + str(satellites_used(gps3_thread.data_stream.satellites)[0]), fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)
        elif curtime == 40:
            with canvas(virtual) as draw:
                show_message(device, datetime.now().strftime('%a %-d %B'), fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)
        else:
            with canvas(virtual) as draw:
                text(draw, (1, 1), now, fill="white", font=proportional(CLOCK_FONT))
                if curtime > 0:              
                    draw.rectangle(((max(curtime-29,1),0),(min(curtime,30),0)), fill="white")
            sleep(0.4)
            
            with canvas(virtual) as draw:
                text(draw, (1, 1), now, fill="white", font=proportional(CLOCK_FONT))
                draw.rectangle(((15,0),(16,7)), fill="black")
                if curtime > 0:
                    draw.rectangle(((max(curtime-29,1),0),(min(curtime,30),0)), fill="white")
                
        while curtime == datetime.now().second:
            sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    
