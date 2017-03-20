import wx
import calibration
from math import *
import driver

class CalibFrame(calibration.MainFrame):
    def __init__(self,parent,driver,is_depth = False):
        '''
        driver: current handler to control the robot
        is_depth: If True, only z-axis is allowed.
        '''
        calibration.MainFrame.__init__(self,parent)
        self.driver = driver     #use this driver to control motor movement
        self.speed_factor = 1
        self.is_depth = is_depth
        self.axis.SetValue(True)

    def arrow(self,event):
        #print event.x, event.y
        d = {}
        change = False
        if self.driver.mode == 'absolute':
            change = True
            self.driver.coordinate('relative', False)
        #if z axis
        if self.axis.GetValue():
            if 79 < event.x < 94 and 9 < event.y < 24:
                d = {'Z':self.speed_factor}
            elif 79 < event.x < 94 and 46 < event.y < 61:
                d = {'Z':-self.speed_factor}
        else:   #if not z axis
            if 79 < event.x < 94 and 9 < event.y < 24:
                d = {'Y':self.speed_factor}
            elif 79 < event.x < 94 and 46 < event.y < 61:
                d = {'Y': -self.speed_factor}
            elif 62 < event.x < 82 and 26 < event.y < 41:
                d = {'X':-self.speed_factor}
            elif 98 < event.x < 112 and 26 < event.y < 42:
                d = {'X':self.speed_factor}
        self.driver.move(d,False)
        if change:
            self.driver.coordinate('absolute',False)

    def multiply10(self,event):
        if self.tenFolds.GetValue():
            self.speed_factor = 10
        else:
            self.speed_factor = 1

    def reset(self,event):
        self.driver.home(False)
        self.Close()

    def z_axis(self,event):
        if self.is_depth:
            self.axis.SetValue(True)

if __name__ == '__main__':
    app = wx.App(False)
    d= driver.Driver()
    try:
        d.connect('COM38','115200')
    except:
        pass

    frame = CalibFrame(None,d,True)
    frame.Show(True)
    app.MainLoop()
    d.disconnect()
    app = None
