from robot import Robot
from pipetter import Pipette
from deck import Point,Well

def main():
    #initialize the trash,tip, pipette and robot
    tip = Point('rack1')
    trash = Point('dustbin1')
    water = Point('water')
    coloring = Point('coloring')
    wellPlate = Well('96WellPlate1',85.48,127.76,9)
    p = Pipette('p20',trash,tip,20)
    r = Robot(p)

    #connect to robot
    r.connect('COM38')
    r.set_speed(200)

    #calibrate position and pipette

    #Write protocol here

    #get distilled water in 9 points
    p.pick_up_tip(tip)
    for i in xrange(9):
        p.aspirate(18,water)
        p.dispense(18,wellPlate[i])
        pass
    #p.drop_tip(trash)

    #get samples to each point and dilute
    #p.pick_up_tip(tip)
    p.aspirate(6,coloring)
    for i in xrange(3):
        p.dispense(2,wellPlate[i*3])
        pass
    #p.drop_tip(trash)
    for j in xrange(0,9,3):
        #p.pick_up_tip(tip)
        for i in xrange(2):
            p.mix(1,location = wellPlate[i+j])
            p.aspirate(2)
            p.dispense(2,wellPlate[i+j+1])
        #p.drop_tip(trash)
    r.run(True)
    print 'Finished'
    r.home()
    r.disconnect()

if __name__ == '__main__':
    main()
