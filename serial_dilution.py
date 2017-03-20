from robot import Robot
from pipetter import Pipette
from deck import Point,Well

def main():
    #initialize the trash,tip, pipette and robot
    tip = Point('tip1')
    trash = Point('trash1')
    sample = Point('sample1')
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
        #p.aspirate(18,sample['A1'])
        #p.dispense(18,wellPlate[i])
        pass
    p.drop_tip(trash)

    #get samples to each point and dilute
    p.pick_up_tip(tip)
    #p.aspirate(6,sample['A2'])
    for i in xrange(3):
        #p.dispense(2,wellPlate[i*3])
        pass
    p.drop_tip(trash)
    for j in xrange(0,9,3):
        p.pick_up_tip(tip)
        for i in xrange(2):
            #p.mix(wellPlate[i+j])
            #p.aspirate(2)
            pass#p.dispense(wellPlate[i+j+1])
        p.drop_tip(trash)
    r.run(True)
    print 'Finished'
    r.home()
    r.disconnect()

if __name__ == '__main__':
    main()
