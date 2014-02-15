import time
import sys

import openGL.GL as gl
import openGL.GLUT as glut

from BCore.Classes.Stations.Station import Station

PPORT_LO = 0
PPORT_HI = 1


class StandardVisionBehaviorStation(Station):
    """
        STANDARDVISIONBEHAVIORSTATION defines a subclass of STATION.
        It defines a station with a standard display, a parallel port for i/o
        with standard pin-out settings, sounds settings which can only be
        turned on or off, three valve pins, three sensor pins
        Attributes allowed are:
            stationID        : numeric ID to be sent to STATION
            stationPath      : DO NOT SEND - STATION WILL SET IT
            display          : dictionary containing details about the
                               display unit
            soundOn          : True/False
            parallelPort     : dictionary containing details about the parallel
                               port

        For the StandardVisualBehaviorStation, with Rev 2/3 breakout boards
        ("The Bomb"), only certain ports are used and for specific purposes:
            Pin 2            :            Right Reward Valve
            Pin 3            :            Center Reward Valve
            Pin 4            :            Left Reward Valve
            Pin 5            :            LED1
            Pin 6            :            eyePuff
            Pin 7            :            LED2
            Pin 8            :            indexPulse
            Pin 9            :            framePulse
            Pin 10           :            Center Response Sensor
            Pin 12           :            Right Response Sensor
            Pin 13           :            Left Response Sensor
        While, these values are not hard coded here, use these values if you
        want your system to work :)

        Use these defaults unless you know what you are doing
        parallelPort = {}
        parallelPort['rightValve'] = 2
        parallelPort['centerValve'] = 3
        parallelPort['leftValve'] = 4
        parallelPort['valvePins'] = (2, 3, 4)
        parallelPort['centerPort'] = 10
        parallelPort['rightPort'] = 12
        parallelPort['leftPort'] = 13
    """

    def __init__(st, **kwargs):
        super(StandardVisionBehaviorStation, st).__init__(
            stationID=kwargs['stationID'])
        st.display = kwargs['display']
        st.soundOn = kwargs['soundOn']
        st.parallelPort = kwargs['parallelPort']
        pPort = st.initializeParallelPort()
        if pPort:
            st.parallelPort['pPort'] = pPort
            st.closeAllValves()
        else:
            st.parallelPort = None

    def closeAllValves(st):
        st.parallelPort['pPort'].writePins(
            st.parallelPort['valvePins'], PPORT_LO)

    def readPorts(st):
        st.parallelPort['pPort'].readPins(
            st.parallelPort['portPins'])

    def openValve(st, valve):
        st.parallelPort['pPort'].writePins(
            st.parallelPort[valve], PPORT_HI)

    def closeValve(st, valve):
        st.parallelPort['pPort'].writePins(
            st.parallelPort[valve], PPORT_LO)

    def flushValves(st, dur):
        st.parallelPort['pPort'].writePins(
            st.parallelPort['valvePins'], PPORT_HI)
        time.sleep(dur)
        st.parallelPort['pPort'].writePins(
            st.parallelPort['valvePins'], PPORT_LO)

    def startGL(st):
        glut.glutInit(sys.argv)
        glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)

    def stopGL(st):
        pass

    def testGL(st):

        def drawTest():
            gl.glClear(gl.GL_CLEAR_BUFFER_BIT)
            glut.glutWireTeapot(0.5)

        st.startGL()
        glut.glutInitWindowSize(250, 250)
        glut.glutInitWindowPosition(100, 100)
        glut.glutCreateWindow("Station Test")
        glut.glutDisplayFunc(drawTest)
        glut.glutMainLoop()

        time.sleep(5)

        glut.glutLeaveMainLoop()

    def getDisplaySize(st):
        pass

    def doTrials(st, bServer, numTrials):
        pass


if __name__ == '__main__':
    # Create a new StandardVisionBehaviorStation and test it
    st = StandardVisionBehaviorStation(stationID=0, display=None, soundOn=False,
                                        parallelPort=None)
    print(('Testing the station\'s graphics'))
    st.testGL()