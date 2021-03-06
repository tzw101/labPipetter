from driver import Driver
from deck import Point,Well
import json
from scipy import stats
import time

class Pipette():

    def __init__(self,name = None, trash_container = None, tip_racks = None, max_volume = 200,aspirate_speed = None,dispense_speed = None):
        ''' Currently, only compiler mode is implemented. All commands will be saved in queue and run with robot.run()

            Parameters:

            name (str): Assigns the pipette a unique name for saving it's calibrations
            trash_container (Container): Sets the default location drop_tip() will put tips (Default: None)
            tip_racks (Container):  A Container for pick_up_tip() (Default: None)
            max_volume (int):  The largest uL volume for this pipette (Default: 200)
            aspirate_speed (int): The speed (in mm/minute) the plunger will move while aspirating (Default: None)
            dispense_speed (int): The speed (in mm/minute) the plunger will move while dispensing (Default: None)
        '''
        self.driver = Driver()
        self.position = {'X':0,'Y':0,'Z':0,'E':0}       #E(positive means pushing down. Negative retracts up)
        self.calibration_plunger = {'m': 0, 'c': 0}   #m and c are slope and gradient of calibration curve respectively
        self.name = name
        self.trash = trash_container
        self.tips = tip_racks
        self.max_volume = max_volume
        self.aspirate_speed = aspirate_speed
        self.dispense_speed = dispense_speed
        self.starting_postion = 180         # absolute z plane. will return to this z before homing

        #retrieve calibration data
        if self.trash or self.tips:
            l =[self.trash,self.tips]
            for each in l:
                calibration = Pipette.read_calibration_data(r'C:\Users\user\Desktop\calibration.data',each.name)
                if calibration:
                    each.coordinate = calibration['coordinate']
                if 'depth' in calibration:
                    each.coordinate = calibration['depth']

    def set_speed(self,mode_speed_pair):
        '''Pass dictionary of mode and speed as key-value pair, eg: {'aspirate':300,'dispense':400}
        If integer is passed in, both aspirate and dispense will have the integer value as the speed'''
        if type(mode_speed_pair) == dict:
            if 'aspirate' in mode_speed_pair:
                self.aspirate_speed = mode_speed_pair['aspirate']
            elif 'dispense' in mode_speed_pair:
                self.dispense_speed = mode_speed_pair['dispense']
            else:
                raise ValueError, 'Dictionary into set_speed() should have aspirate or dispense'
        elif type(mode_speed_pair) == int:
            self.aspirate_speed = mode_speed_pair
            self.dispense_speed = mode_speed_pair
        else:
            raise TypeError, 'Wrong type is passed in.'

    def home(self,enqueue = True):
        '''This function will only home the position of x and y of pipette'''
        self.driver.move({'X':0,'Y':0},enqueue)
        if enqueue == False:
            self.position['X'] = 0
            self.position['Y'] = 0

    def calibrate(self,max_volume = 200, number_of_tries = 5):
        '''
        Calibrate the plunger position. Use DI water to calibrate. Initially plunger is at zero position (maximum volume)
        Max_volume: The maximum volume written on the pipette. Default (200)
        Number of tries: Number of data points to be obtained. Default (5)
        '''
        #Implement by changing the extrusion and obtaining the volume. Linear best fit line is drawn and the relationship is saved.
        usage = ('Usage: Place DI water container below the pipette tip. The pipette will aspirate certain amount of DI water. '
                 'When prometed, use electronic balance to measure the mass of water aspirated. Input the mass. This process will '
                 'repeat for 5 times by default. The number of data points can be changed by argument. The calibrated data will be'
                 'saved automatically')
        print usage

        extrusion = 5
        interval = 1
        data = {}
        for i in xrange(number_of_tries):
            to_quit = raw_input('Place DI water beneath pipette tip. Make sure pipette tip is immersed. Press any key to continue. Press q/Q to stop')
            if type(to_quit) == str and to_quit.lower() == 'q':      #check for user input here. Must be string
                print 'Calibration stopped'
                return
            self.driver.extrude(-extrusion,False)
            self.driver.delay(0.5,False)
            self.driver.extrude(extrusion,False)
            raw_input('Place electronic balance beneath the tip to measure the mass of DI aspirated. Press any key to continue')
            self.driver.extrude(-extrusion*1.2,False)
            mass = raw_input(' Type in the mass measured. Press q/Q to stop')
            self.driver.extrude(extrusion*1.2,False)
            if mass.lower() == 'q':      #check for user input here. Must be string
                print 'Calibration stopped'
                return
            try:
                mass = float(mass)
                print 'Mass: '+str(mass)
                data[extrusion] = mass
            except:
                raise ValueError,'Please input appropriate value. Only numbers or q can be entered'

            if i == 2:          #the extrusion rebalancing to prevent maximum volume is exceeded. If put >, subsequent reading will have rebalancing
                slope, intercept, r_value, p_value, std_err = stats.linregress(data.keys(),data.values())
                predicted_max_volume = slope*(extrusion+number_of_tries*interval)+intercept     #y = mx+c. number of tries times interval is the maximum extrusion
                print slope, intercept,predicted_max_volume
                return
                if predicted_max_volume >= max_volume:
                    interval = (max_volume-intercept)/(slope*number_of_tries)  #The lower value is used. Double check.
            else:
                extrusion += interval
            print interval

        if len(data) != number_of_tries:
            raise Exception, 'Something wrong happened during calibration'

        slope, intercept, r_value, p_value, std_err = stats.linregress(data.keys(),data.values())
        if r_value ** 2 < 0.90:
            to_quit = raw_input('The R2 value obtained is %f. Do you want to proceed? Press q/Q to quit. Rerun calibration afterwards.' % r_value)
            if type(to_quit) == str and to_quit.lower() == 'q':      #check for user input here. Must be string
                print 'Calibration stopped due to low R2.'
                return
        self.calibration_plunger['m'] = slope
        self.calibration_plunger['c'] = intercept

        if self.name:
            calibration = {}
            calibration[self.name] = self.calibration_plunger
            Pipette.save_calibration_data(r'C:\Users\user\Desktop\plunger.data',calibration)
            print 'Calibration saved to C:\Users\user\Desktop\plunger.data'


    def calibrate_position(self,location):
        '''
        Calibrate the position of container with respect to home position of pipette
        Location is the container object, either Point or Well.
        '''
        usage = ('Usage: Move the pipette to the origin of the container. For well,\n'
                 'it is the A1 position. For point it is the center of the circle.\n\n'
                 'Press q or Q to exit but saving position.\n'
                 'Press r or R to exit but without saving position.\n\n'
                 'Y-axis:\n'
                 'w: Move up\n'
                 's: Move down\n\n'
                 'X-axis:\n'
                 'a: Move left\n'
                 'd: Move right\n\n'
                 'Z-axis:\n'
                 'u: Move up\n'
                 'j: Move down\n\n'
                 'Upper case: move by 10mm\n'
                 'Lower case: move by 1mm\n')
        print usage

        #Initiate the driver, need to implement this later.
        #if self.driver == None:
        #    self.driver.connect()
        self.driver.home(False)
        self.driver.coordinate('relative',False)

        while True:
            d = {}
            key = raw_input('Press key to move')
            if key.lower() == 'w':
                d = {'Y':1}
            elif key.lower() == 's':
                d = {'Y':-1}
            elif key.lower() == 'a':
                d = {'X':1}
            elif key.lower() == 'd':
                d = {'X':-1}
            elif key.lower() == 'u':
                d = {'Z':1}
            elif key.lower() == 'j':
                d = {'Z':-1}
            elif key.lower() == 'q':
                break
            elif key.lower() == 'r':
                print 'Terminated without saving'
                return
            else:
                print 'Invalid key entered'
            if d:
                for each in d:
                    if key.isupper():
                        d[each] *= 10
                    if each == 'X':
                        self.position['X']+=d[each]
                    if each == 'Y':
                        self.position['Y'] += d[each]
                    if each == 'Z':
                        self.position['Z'] += d[each]
                self.driver.move(d,False)

        if location.coordinate == None:
            location.coordinate = {'X':0,'Y':0,'Z':0}

        if type(location) == Well:
            for point in location.points:
                for axis in point.coordinate:
                    point.coordinate[axis] += self.position[axis]       #check for bug. If position dictionary and point coordinate dict is different.
        elif type(location) == Point:
            for axis in location.coordinate:
                location.coordinate[axis] += self.position[axis]

        #Now calibrating depth
        z = self.position['Z']
        while True:
            print 'Now calibrating depth of location. Press J to move down, U to move up. q/Q to quit with saving. r/R to quit without saving.'
            key = raw_input('Press key to move')
            if key.lower() == 'u':
                d = {'Z':1}
            elif key.lower() == 'j':
                d = {'Z':-1}
            elif key.lower() == 'q':
                break
            elif key.lower() == 'r':
                yes = raw_input('Terminate without calibrating depth? Press 0 to return without saving anything.')
                if yes == 0:
                    return
                else:
                    print 'Invalid key entered'
            else:
                print 'Invalid key entered'
            if d:
                if key.isupper():
                    d['Z'] *= 10
                self.position['Z'] += d['Z']
                self.driver.move(d,False)

        depth = self.position['Z']-z        #check again
        if depth < 0:
            print 'Depth should be positive'
        location.depth = depth

        if self.name:
            coordinate = {}
            #pip = {}
            coordinate[location.name] = {'coordinate':location.coordinate,'depth':location.depth}
            #pip[self.name]={'Position':coordinate}
            Pipette.save_calibration_data(r'C:\Users\user\Desktop\calibration.data',coordinate)
            print 'Calibration saved to C:\Users\user\Desktop\calibration.data'

    @staticmethod
    def save_calibration_data(path,coordinate):
        #check this section again. This may need quite some buffer as the calibration data is deleted and recreated during every calibration
        #need to have error checking code
        try:
            with open(path,'r') as calibration:
                old_data = calibration.read()
                new_data = json.loads(old_data)
                for each in coordinate:
                    if each in new_data:
                        del new_data[each]
                new_data.append(coordinate)
        except IOError:
            new_data = coordinate

        with open(path,'w') as calibration:
            s = json.dumps(new_data)
            calibration.write(s)

    @staticmethod
    def read_calibration_data(path,name):
        with open(path,'r') as calibration:
            data = json.loads(calibration.read())
            if name in data:
                return data[name]
            else:
                return None

    #may convert this into decorator
    def get_calibration_data(self,path):
        if self.calibration_plunger['m'] or self.calibration_plunger['c']:
            return
        with open(path) as calibration:
            data = json.loads(calibration.read())
            if self.name in data:
                self.calibration_plunger = data[self.name]
            else:
                return          #try to implement message telling user that the pipette has not been calibrated

    def calculate_extrusion(self,volume):
        self.get_calibration_data(r'C:\Users\user\Desktop\plunger.data')
        return (volume-self.calibration_plunger['c'])/self.calibration_plunger['m']

    def aspirate(self,volume = None,location = None,rate = 1.0,enqueue = True):  #havent moved up
        ''' Aspirate a volume of liquid (in microliters/uL) using this pipette
            volume: default pipette max volume
            location: Point or well object. Well is iterable.
            rate: Set plunger speed for this aspirate, where speed = rate * aspirate_speed
        '''
        if volume == None:
            volume = self.max_volume
        self.driver.coordinate('relative',enqueue)
        if location:
            self.driver.move(location.coordinate,enqueue)
            self.driver.move({'Z':location.depth})
        else:
            self.driver.move({'Z':2})       #default to 2mm. check whether this should be open as parameters.
        extrusion = self.calculate_extrusion(volume)
        self.driver.extrude(extrusion)
        self.driver.delay(0.5)
        self.driver.extrude(-extrusion)
        #moving back up
        if location:
            self.driver.move({'Z':-location.depth})
        else:
            self.driver.move({'Z':-2})

    def dispense(self,volume = None,location = None,rate = 1.0,enqueue = True):
        if volume == None:
            volume = self.max_volume
        self.driver.coordinate('relative',enqueue)
        if location:
            self.driver.move(location.coordinate,enqueue)
        extrusion = self.calculate_extrusion(volume)
        self.driver.extrude(-extrusion)

    def mix(self,repetitions = 3, volume = None, location = None, rate = 1.0,enqueue = True ):
        '''Mix volume of liquid'''
        if volume == None:
            volume = self.max_volume
        self.driver.coordinate('relative',enqueue)
        if location:
            self.driver.move(location.coordinate,enqueue)
            self.driver.move({'Z':location.depth})
        else:
            self.driver.move({'Z':2})
        extrusion = self.calculate_extrusion(volume)
        for i in xrange(repetitions):
            self.driver.extrude(extrusion)
            self.driver.delay(0.5)
            self.driver.extrude(-extrusion)
            self.driver.delay(0.5)
        #moving back up
        if location:
            self.driver.move({'Z':-location.depth})
        else:
            self.driver.move({'Z':-2})

    def blow_out(self,location = None,enqueue = True):   #Error in code below
        '''Blow_out will eject all liquid. Hence if there is liquid inside, do not use blow_out as it will result in inaccurate volume'''
        if location:
            self.driver.move(location,enqueue)
        extrusion = self.calculate_extrusion(self.max_volume)+1
        self.driver.extrude(extrusion)
        self.driver.extrude(-extrusion)

    def move_to(self,location,strategy = 'arc', enqueue= True):
        '''Move pipette to position of point of well'''
        self.driver.coordinate('relative',enqueue)
        self.driver.move(location.coordinate,enqueue)       #strategy of movement not yet implemented

    def pick_up_tip(self,location = None,enqueue = True):
        self.driver.coordinate('relative',enqueue)
        if location:
            self.driver.move(location.coordinate,enqueue)
            self.driver.move({'Z':location.depth})
            self.driver.delay(0.5)
            self.driver.move({'Z':-location.depth})
        else:
            self.driver.move({'Z':2})
            self.driver.delay(0.5)
            self.driver.move({'Z':-2})

    def drop_tip(self,location = None, enqueue = True):
        self.driver.coordinate('relative',enqueue)
        if location:
            self.driver.move(location.coordinate,enqueue)
            self.driver.move({'Z':location.depth})
            self.driver.delay(0.5)
            self.driver.move({'Z':-location.depth})
        else:
            self.driver.move({'Z':2})
            self.driver.delay(0.5)
            self.driver.move({'Z':-2})

    def return_tip(self):
        '''This method has not been implemented, as only one tip rack is provided'''
        pass
