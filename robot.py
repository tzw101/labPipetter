from driver import Driver
from pipetter import Pipette
import time

class Robot(object):

    def __init__(self,instrument = None):
        '''
        Pass the pipette object. If no instrument is attached, connect function or those that use driver won't function properly
        '''
        self.instrument = instrument
        self.is_connected = False
        if instrument == None:
            self.driver = None
        else:
            try:
                self.driver = self.instrument.driver
            except Exception:
                raise ValueError,'Invalid instrument attached. Currently only pipette is supported. Ensure that the instrument has driver attribute'

    def add_instrument(self,instrument):
        self.instrument = instrument
        try:
            self.driver = self.instrument.driver
        except Exception:
            raise ValueError,'Invalid instrument attached. Currently only pipette is supported. Ensure that the instrument has driver attribute'

    def connect(self,port=None):
        '''If port is not provided, COM38 will be assumed. Currently baud rate is fixed at 115200'''
        if not port:
            port = 'COM38'
        self.driver.connect(port,115200)
        self.is_connected = self.driver.online
        print 'Robot connected to port '+port+' at baud rate of 115200'

    def disconnect(self):
        self.driver.disconnect()
        print 'Robot disconnected'

    def force_stop(self):
        self.driver.force_stop()
        print 'Robot forced stop'

    def home(self):
        if self.instrument:
            self.instrument.home(False)
        self.driver.home(False)

    def status(self):
        if self.driver.printing():
            return 'Printing...'
        else:
            return 'Idle'

    def pause(self):
        if self.driver.pause():
            print 'Paused'
        else:
            print 'Device is not pipetting'

    def resume(self):
        if self.driver.resume():
            print 'Resumed'
        else:
            print 'Device is already running'

    def commands(self):
        '''
        Show the names of all commands in the command queue
        '''
        print self.driver.command_name

    def reset(self):
        self.driver.reset_command()

    def reset_instrument(self):
        self.instrument = None
        self.driver = None
        self.is_connected = False

    def run(self,hang = False):
        self.driver.home(False)
        self.driver.move({'Z':self.instrument.starting_position},False)
        self.driver.run()
        if hang:
            for i in xrange(300):
                if self.driver.printing():
                    time.sleep(1)
                else:
                    break

    def set_speed(self,speed):
        '''
        Speed - percentage of current speed. If double the current speed, type 200. Maximum is 300
        '''
        if int(speed) > 300:
            raise RuntimeError('Maximum speed is 300. Too high will cause excessive vibration')
        self.driver.set_speed(speed,False)

