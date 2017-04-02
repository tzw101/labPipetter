from robot import Robot
from pipetter import Pipette
from deck import Point

def main():
    #initialize the trash,tip, pipette and robot
    source = Point('source')
    destination = Point('destination')
    p = Pipette('p20',20)
    r = Robot(p)

    #connect to robot
    r.connect('COM38')
    r.set_speed(200)

    #calibrate position and pipette

    #Write protocol here

    #get distilled water from source to destination
    #p.pick_up_tip(tip)
    for i in xrange(10):
        p.aspirate(18,source)
        p.dispense(18,destination)

    #get di from destination to source
    for i in xrange(10):
        p.aspirate(18,source)
        p.dispense(18,destination)

    while True:
        try:
            r.run(True)
            print 'Finished'
            r.home()
        except:
            r.disconnect()
            print 'Terminated'
            break

if __name__ == '__main__':
    main()