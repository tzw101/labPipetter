from printrun.printcore import printcore
from printrun import gcoder

class Driver():

    def __init__(self):
        '''
        This class contains gcode wrapper needed only for this project.
        The list of gcode command can be passed into printcore to run
        '''
        self.command_queue = []         #list of command
        self.p = None                   #printer handler
        self.printing = False
        self.command_name = []

    def connect(self,port,baud_rate):
        '''p.printcore('COM3',115200) on Windows'''
        self.p = printcore(port,baud_rate)
        self.printing = self.p.printing

    def run(self):
        '''Run commands in command queue'''
        if self.command_queue == []:
            print 'Command Queue is empty. Put some commands to continue'
            return
        gcode = gcoder.LightGCode(self.command_queue)
        if not self.p:
            raise RuntimeError, 'Printer is not connected'
        if self.printing:
            raise Exception, 'Printer is already started. Only one instance is allowed.'
        self.p.startprint(gcode)

    def send_command(self,command):
        '''Send command manually. Command must be valid gcode string'''
        self.p.send_now(command)

    def pause(self):
        if not self.printing:
            return False
        if not self.is_paused:
            self.p.pause()
            return True
        else:
            return False

    def resume(self):
        if not self.printing:
            return False
        if self.is_paused:
            self.p.resume()
            return True
        else:
            return False

    def disconnect(self):
        if not self.printing:
            self.p.disconnect()
            self.reset()
        else:
            return 'Code is still running. Use force_stop to stop'

    def force_stop(self):
        self.p.disconnect()
        self.reset()

    def reset(self):
        self.printing = False
        self.p = None
        self.reset_command()

    def reset_command(self):
        self.command_queue = []
        self.command_name = []

    def set_speed(self,speed):
        self.send_command("M220 S" + int(speed))

    def set_feedrate(self,speed):
        '''
        Set the feedrate of extruder only.
        '''
        #check this command again. M221. And maybe implement for x y and z as well for m203
        self.send_command("M203 E" + int(speed))

    def move(self,position,enqueue = True):
        '''Parameters
        ----------------------
        axis: X,Y,Z
        distance: in mm

        Pass in dictionary even if the movement is along one axis
        '''
        if type(position) != dict:
            raise TypeError, 'Only dictionary is accepted'
        string = ''
        for axis,distance in position.iteritems():
            axis = axis.upper()
            if axis not in ['X','Y','Z']:
                raise Exception, 'Only x, y and z axis are allowed'
            string += axis
            if type(distance) in [int,str]:
                string += str(distance)
                string += ' '
            else:
                raise TypeError, 'Distance must be integer'
        if enqueue:
            self.command_queue.append('G1 '+string)
            self.command_name.append('Move to position '+str(position))
            return 'G1 '+string+'\n'
        else:
            self.send_command('G1 '+string)

    def home(self,enqueue = True):
        self.move({'X':0,'Y':0},enqueue)
        if enqueue:
            self.command_queue.append('G28')
            self.command_name.append('Home')
            return 'G28\n'
        else:
            self.send_command('G28')

    def extrude(self,distance, enqueue = True):
        string = 'E'+str(distance)
        if enqueue:
            self.command_queue.append('G1 '+string)
            self.command_name.append('Extrude by '+str(distance)+'mm')
            return 'G1 '+string+'\n'
        else:
            self.send_command('G1 '+string)

    def coordinate(self,mode = 'absolute',enqueue = True):
        '''Parameters
           -----------------------
           mode : absolute or relative
           (choose absolute or relative reference frame)
        '''
        if mode == 'absolute':
            if enqueue:
                self.command_queue.append('G90')
                self.command_name.append('Set coordinate to absolute')
                return 'G90\n'
            else:
                self.send_command('G90')
        elif mode == 'relative':
            if enqueue:
                self.command_queue.append('G91')
                self.command_name.append('Set coordinate to relative')
                return 'G91\n'
            else:
                self.send_command('G91')
        else:
            raise Exception, 'Invalid mode for reference frame'

    def delay(self,time,enqueue = True):
        '''Parameters
        --------------------
        time: in seconds
        '''
        if enqueue:
            self.command_queue.append('G4 S'+str(time))
            self.command_name.append('Delay for '+str(time)+'s')
            return 'G4 S'+str(time)+'\n'
        else:
            self.send_command('G4 S'+str(time))