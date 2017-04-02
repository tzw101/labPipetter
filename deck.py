from pipetteIO import *
import os

class Point(object):

    def __init__(self,name,coordinate = None,solution = None, depth = None):
        ''' Name: Each point must have a name for proper reference.
            Coordinate (dictionary): x,y coordinate of the center of point (default: None)
            Solution (string): content of the container (default: None)
            Depth (float): distance from top to bottom of the point (default None)'''
        if coordinate and type(coordinate) == dict:
            self.coordinate = coordinate
        elif coordinate:
            raise TypeError, 'Wrong input argument format'
        else:
            self.coordinate = None
        self.name = name
        self.solution = solution
        self.depth = depth          #depth and coordinate can be passed by after calibration by pipete instance
        self.is_calibrated = False

        if self.name:
            try:
                calibration = read_calibration_data(os.getcwd()+'\\calibration.data',self.name)
                if calibration:
                    self.coordinate = calibration['coordinate']
                    if 'depth' in calibration:
                        self.depth = calibration['depth']
                    self.is_calibrated = True
            except IOError:
                print 'No calibration.data file found'

class Well(object):

    def __init__(self,name,width,length, spacing,coordinate = None,number_of_rows = 8,number_of_columns = 12,depth = None):
        '''
        Only rectangular well is supported.
        Well origin is at A1 corner.

        Name: each well must have name for reference
        Width: width of plate
        Length: length of plate
        Spacing: spacing between center of two points
        Number of rows and columns: Default to 8 and 12 for 96-well plate

                                Length (x)
                --------------------------------------------------
        width   |
        (y)     |
                |
                |
                |
                |
                |
        '''
        self.name = name
        self.depth = depth
        self.spacing = {'row':[spacing]*8,'column':[spacing]*12}
        self.number_of_rows = number_of_rows
        self.number_of_columns = number_of_columns
        self.width = width
        self.length = length
        self.is_calibrated = False

        if coordinate:
            self.coordinate = coordinate
        else:
            self.coordinate = {'X':0,'Y':0,'Z':0}

        #self.corners = {'tl':self.coordinate,'tr':{'X':self.length,'Y':0,'Z':0},'bl':{'X':0,'Y':self.width,'Z':0},'tr':{'X':self.length,'Y':self.width,'Z':0}}

        if self.name:
            try:
                calibration = read_calibration_data(os.getcwd()+'\\calibration.data',self.name)
                if calibration:
                    self.coordinate = calibration['coordinate']
                    if 'depth' in calibration:
                        self.depth = calibration['depth']
                    if 'spacing' in calibration:
                        self.spacing = calibration['spacing']   #structure of spacing in calibration dict. calibration[spacing] has two keys. spacing and number
                    self.is_calibrated = True
            except IOError:
                print 'No calibration.data file found'


        self.points = []            #list of Point object

        alphabet = list('abcdefghijklmnopqrstuvwxyz'.upper())
        x,y = 0,0                   #assume first well is at (0,0)

        #interval = number_of_columns/self.spacing['column']['applied_to']

        for row in xrange(number_of_rows):
            for column in xrange(1,number_of_columns+1):
                point = Point(alphabet[row]+str(column),{'X':self.coordinate['X']+x,'Y':self.coordinate['Y']+y,'Z':self.coordinate['Z']},depth = self.depth)
                self.points.append(point)
                x += self.spacing['column'][column-2]
            x = 0
            y += self.spacing['row'][row]

    '''
        if self.points[number_of_columns-1].coordinate['X'] > length:
            raise ValueError, 'Length of well is too short to accomodate this number of wells'
        elif self.points[(number_of_rows-1)*number_of_columns].coordinate['Y'] > width:
            raise ValueError, 'Width of well is too short to accomodate this number of wells'
    '''
    def error_correction(self):
        pass

    def dict_of_coordinates(self):
        d = {}
        for point in self.points:
            d[point.name] = point.coordinate
        return d

    def __iter__(self):
        return

    def __getitem__(self,key):
        for point in self.points:
            if point.name == key:
                return point
        if type(key) == int:
            try:
                return self.points[key]
            except Exception as e:
                raise e

