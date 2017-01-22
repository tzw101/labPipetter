from driver import Driver
from pipetter import Pipette
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
        self.driver.home()

    def status(self):
        if self.driver.printing:
            return 'Printing...'
        else:
            return 'Idle'

    def pause(self):
        if self.pause():
            print 'Paused'
        else:
            print 'Device is not pipetting'

    def resume(self):
        if self.resume():
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

    def run(self):
        self.driver.run()



