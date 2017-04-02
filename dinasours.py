'''Protocol o saurus'''
from robot import Robot
from pipetter import Pipette
from deck import Point,Well

def main():
    #initialize the trash,tip, pipette and robot
    coloring = Point('coloring')
    wellPlate = Well('96WellPlate1',85.48,127.76,9)
    p = Pipette('p20')
    r = Robot(p)

    #connect to robot
    r.connect('COM38')
    r.set_speed(200)

    #calibrate position and pipette

    #Write protocol here
    holes = 'D1 E1 D2 E2 D3 E3 F3 G3 H3 C4 D4 E4 F4 G4 H4 C5 D5 E5 F5 G5 C6 D6 E6 F6 G6 C7 D7 E7 F7 G7 D8 E8 F8 G8 H8 E9 F9 G9 H9 F10 G11 H12'.split(' ')
    redholes = 'C3 B4 B5 B6 B7 A5 A7 C8 C9 D9 E10 E11 F11 G12'.split(' ')

    for hole in holes:
        p.aspirate(18,coloring)
        p.dispense(18,wellPlate[hole])

    p.driver.delay(10,True)
    for red in redholes:
        p.aspirate(18,coloring)
        p.dispense(18,wellPlate[red])

    r.run(True)
    print 'Finished'
    r.home()
    r.disconnect()

if __name__ == '__main__':
    main()
