from pipetter import Pipette
from deck import Point,Well
from driver import Driver

import time

def demo_movement():
    d = Driver()
    try:
        d.connect('COM38',115200)
    except:
        print 'Error again when connect'
    d.home()
    d.command_queue.append('M220 S400')
    d.move({'Z':150})
    for i in xrange(20):
        d.move({'X':20})
        d.move({'Y':20})
        d.move({'X':-20})
        d.move({'Y':-20})
        d.move({'X':0,'Y':0})
        d.move({'Z':160})
        d.move({'Z':140})
        d.move({'Z':150})
        time.sleep(1)
    d.home()

    while True:
        try:
            d.run()
            time.sleep(10)
        except KeyboardInterrupt:
            d.disconnect()
            print 'Demo stopped'
            break

def demo_pipetting():
    pass


