from printrun.printcore import printcore
from printrun import gcoder
import time

class Driver():

    def __init__(self):
        '''
        This class contains gcode wrapper needed only for this project.
        The list of gcode command can be passed into printcore to run
        '''
        self.command_queue = []         #list of command
        self.p = None                   #printer handler
        self.command_name = []
        self.servo_angle = 0
        self.position = {'X':0,'Y':0,'Z':230}
        self.mode = 'absolute'
        self.online = False

    def connect(self,port,baud_rate):
        '''p.printcore('COM3',115200) on Windows'''
        self.p = printcore(port,baud_rate)
        self.position = {'X':0,'Y':0,'Z':230}       #check if this is redundant
        time.sleep(5)
        self.home(False)
        self.online = self.p.online

    def run(self,clear_queue = False):
        '''Run commands in command queue'''
        if self.command_queue == []:
            print 'Command Queue is empty. Put some commands to continue'
            return
        gcode = gcoder.LightGCode(self.command_queue)
        if not self.p:
            raise RuntimeError, 'Printer is not connected'
        if self.printing():
            raise Exception, 'Printer is already started. Only one instance is allowed.'
        self.p.startprint(gcode)
        if clear_queue:
            self.reset_command()

    def send_command(self,command):
        '''Send command manually. Command must be valid gcode string'''
        self.p.send_now(command)

    def printing(self):
        return self.p.printing

    def pause(self):
        if not self.printing():
            return False
        if not self.is_paused:
            self.p.pause()
            return True
        else:
            return False

    def resume(self):
        if not self.printing():
            return False
        if self.is_paused:
            self.p.resume()
            return True
        else:
            return False

    def disconnect(self):
        if not self.printing():
            self.p.disconnect()
            self.reset()
        else:
            return 'Code is still running. Use force_stop to stop'

    def force_stop(self):
        self.p.disconnect()
        self.reset()

    def reset(self):
        self.p = None
        self.reset_command()
        self.position = {'X':0,'Y':0,'Z':230}
        self.online = False

    def reset_command(self):
        self.command_queue = []
        self.command_name = []
        self.position = {'X':0,'Y':0,'Z':230}

    def set_speed(self,speed,enqueue = True):
        '''
        speed: specify the speed in terms of percentage. If same as default speed, use 100. If double the default speed, use 200.
        Maximum speed is 300. High speed will cause lots of vibration and inaccuracy. (Hardcoded)
        After the speed is set, it will not be changed until it is disconnected
        '''
        if int(speed) > 300:
            raise RuntimeError('Maximum speed is 300')
        if enqueue:
            self.command_queue.append("M220 S" + str(speed))
            self.command_name.append('Set speed to '+str(speed) + '%')
            return 'G1 '+string+'\n'
        else:
            self.send_command("M220 S" + str(speed))

    def set_feedrate(self,speed):
        '''
        This method is deprecated
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
        Even though enqueue is true, position will also be updated accordingly
        '''
        if type(position) != dict:
            raise TypeError, 'Only dictionary is accepted'
        string = ''
        for axis,distance in position.iteritems():
            axis = axis.upper()
            if axis not in ['X','Y','Z']:
                raise Exception, 'Only x, y and z axis are allowed'
            string += axis
            if type(distance) in [int,float,str]:
                string += str(distance)
                string += ' '
            else:
                raise TypeError, 'Distance must be integer'
            if self.mode == 'absolute':
                self.position[axis] = distance
            elif self.mode == 'relative':
                self.position[axis] += distance
        if enqueue:
            self.command_queue.append('G1 '+string)
            self.command_name.append('Move to position '+str(position))
            return 'G1 '+string+'\n'
        else:
            self.send_command('G1 '+string)

    def home(self,enqueue = True):
        change = False
        if self.mode == 'relative':
            change = True
            self.coordinate('absolute',enqueue)
        self.move({'X':0,'Y':0},enqueue)
        if enqueue:
            self.command_queue.append('G28')
            self.command_name.append('Home')
            return 'G28\n'
        else:
            self.send_command('G28')
        self.position = {'X':0,'Y':0,'Z':230}
        if change:
            self.coordinate('relative',enqueue)

    def extrude(self,distance, enqueue = True):
        '''This method has been deprecated. Use rotate() instead using angle instead of distance. Currently the angle is fixed to 90 degree which is max volume
        '''
        if distance < 0:
            return self.rotate(0,enqueue = enqueue)
        else:
            return self.rotate(90,enqueue = enqueue)
        self.coordinate('relative',enqueue)
        string = 'E'+str(distance)
        if enqueue:
            self.command_queue.append('G1 '+string)
            self.command_name.append('Extrude by '+str(distance)+'mm')
            self.coordinate('absolute',enqueue)
            return 'G1 '+string+'\n'
        else:
            self.send_command('G1 '+string)
            self.coordinate('absolute',enqueue)

    def rotate(self,angle,coordinate = 'absolute',enqueue = True):
        '''
        Use angle between 0 and 90. DO NOT EXCEED to prevent damage to servo
        angle must be INTEGER as it is not sensitive enough to cater for decimal angles
        Delay must be added when rotating as the servo has different command set from the gcode (check again)
        '''
        #absolute or relative positioning
        if int(angle) > 90:
            raise RuntimeError('Maximum angle is 90')
        if coordinate == 'absolute':
            angle = int(angle) + 90 #90 is hardcoded into the program as initial position is 90 degree.
        elif coordinate == 'relative':
            angle += self.servo_angle
        self.servo_angle = angle
        if enqueue:
            self.command_queue.append('M280 P0 S'+str(angle))     #change the servo number if needed
            self.command_name.append('Rotate by '+str(angle)+' degree')
            return 'M280 P0 S'+str(angle)+'\n'
        else:
            self.send_command('M280 P0 S'+str(angle))

    def coordinate(self,mode = 'absolute',enqueue = True):
        '''Parameters
           -----------------------
           mode : absolute or relative
           (choose absolute or relative reference frame)
        '''
        if mode == 'absolute':
            self.mode = 'absolute'
            if enqueue:
                self.command_queue.append('G90')
                self.command_name.append('Set coordinate to absolute')
                return 'G90\n'
            else:
                self.send_command('G90')
        elif mode == 'relative':
            self.mode = 'relative'
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