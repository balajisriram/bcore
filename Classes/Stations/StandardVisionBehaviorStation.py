import time
import os
import psychopy

from .Station import Station
from ..Hardware.Displays import StandardDisplay
from ..Hardware.Ports import StandardParallelPort, TCPServerConnection, BehaviorClientConnection
from ... import get_base_directory

PPORT_LO = 0
PPORT_HI = 1


class StandardVisionBehaviorStation(Station):
    """
        STANDARDVISIONBEHAVIORSTATION(SVBS) defines a subclass of STATION.
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
        parallel_port = {}
        parallel_port['right_valve'] = 2
        parallel_port['center_valve'] = 3
        parallel_port['left_valve'] = 4
        parallel_port['valve_pins'] = (2, 3, 4)
        parallel_port['center_port'] = 10
        parallel_port['right_port'] = 12
        parallel_port['left_port'] = 13
        parallel_port['port_pins'] = (12, 10, 13)
        parallel_port['index_pin'] = 8
        parallel_port['frame_pin'] = 9
        parallel_port['led_0'] = 5
        parallel_port['led_1'] = 7
    """
    display = None
    sound_on = False
    parallel_port_conn = None
    parallel_port = None
    server_connection = None
    session = None

    def __init__(self, display=StandardDisplay, sound_on=False, station_id= 0, station_name='Station0',
                 station_location=(0,0,0), pport_addr='D010', parallel_port='standardVisionBehaviorDefault'):
        super(StandardVisionBehaviorStation, self).__init__(station_id=station_id, station_name=station_name,
                                                          station_location=station_location)
        self.display = display
        self.sound_on = sound_on
        self.parallel_port_conn = StandardParallelPort(pPortAddr=pport_addr)
        self.parallel_port = parallel_port
        pPort = self.initialize_parallel_port()
        if pPort:
            self.parallel_port = pPort
            self.close_all_valves()
        else:
            self.parallel_port = None
            self.server_connection = []

    def initialize_parallel_port(self):
        if self.parallel_port == 'standardVisionBehaviorDefault':
            pPort = {}
            pPort['right_valve'] = 2
            pPort['center_valve'] = 3
            pPort['left_valve'] = 4
            pPort['valve_pins'] = (2, 3, 4)
            pPort['center_port'] = 10
            pPort['right_port'] = 12
            pPort['left_port'] = 13
            pPort['port_pins'] = (12, 10, 13)
            pPort['index_pin'] = 8
            pPort['frame_pin'] = 9
            pPort['led_0'] = 5
            pPort['led_1'] = 7
            return pPort
        else:
            return None # need to write code that checks if allowable

    def run(self):
        # currently just show a splash
        self.splash()
        self.connect_to_server()

    def initialize_display(self):
        pygame.display.init()
        pygame.display.list_modes(depth=0, flags=pygame.FULLSCREEN)

    def connect_to_server(self):
        """
            This is a somewhat complicated handshake. Initially, the
            station acts as a server exposing its IP::port to the server.
            Since the server knows this IP::port it can create a client
            connection easily. Upon connection, BServer(currently client)
            sends a connection info for a separate connection(BServer will
            reserve the space for this connection) to the station and the
            station will connect to the BServer now as a client. This way
            new stations can be added to the server without any
            station-side code modification. BServer can dynamically manage
            its resources. Along with threaded TCP server connections on
            the server side, this should provide scalable, TCP communications
            with the server
        """
        self.server_connection = TCPServerConnection(ipaddr=self.IPAddr,
            port=self.port)
        self.BServerConnection.start()
        BServerConnDetails = self.BServerConnection.recvData()
        # use BServerConnDetails to connect to the BServer as a client
        print('Closing connection as server...')
        self.BServerConnection.stop()
        self.BServerConnection = BehaviorClientConnection(
            ipaddr=BServerConnDetails['ipaddr'],
            port=BServerConnDetails['port'])
        print(('Starting connection as client...'))
        self.BServerConnection.start()

    def get_subject(self):
        """
            For STANDARDVISIONBEHAVIORSTATION.GETSUBJECT(), get data from
            BServer
        """
        raise NotImplementedError()

    def close_all_valves(self):
        self.parallelPort['pPort'].writePins(
            self.parallelPort['valvePins'], PPORT_LO)

    def read_ports(self):
        self.parallelPort['pPort'].readPins(
            self.parallelPort['portPins'])

    def open_valve(self, valve):
        self.parallelPort['pPort'].writePins(
            self.parallelPort[valve], PPORT_HI)

    def close_valve(self, valve):
        self.parallelPort['pPort'].writePins(
            self.parallelPort[valve], PPORT_LO)

    def flush_valves(self, dur):
        self.parallelPort['pPort'].writePins(
            self.parallelPort['valvePins'], PPORT_HI)
        time.sleep(dur)
        self.parallelPort['pPort'].writePins(
            self.parallelPort['valvePins'], PPORT_LO)

    def splash(self):
        pygame.init()
        size = width, height = 600, 400

        screen = pygame.display.set_mode(size)
        splashTex = pygame.image.load(os.path.join(
            getBaseDirectory(), 'BCore', 'Util', 'Resources', 'splash.png'))

        screen.blit(splashTex, [0, 0])
        pygame.display.flip()

        time.sleep(1)

    def get_display_size(self):
        pass

    def get_session(self):
        """
            Connect to BServer and request session details to be loaded
        """
        pass

    def get_compiled_records(self):
        """
            Connect to BServer and request compiledRecords
        """
        return None

    def decache(self):
        """
            Remove session specific details. ideal for pickling
        """
        pass

    def do_trials(self, **kwargs):
        # first step in the running of trials. called directly by station
        # or through the BServer
        if __debug__:
            pass

        # find the subject
        self.get_session()
        cR = self.get_compiled_records()

        Quit = False

        # session starts here
        sR = VisionBehaviorSessionRecord()  # make new session record

        while not Quit and not self.session.stop():
            # it loops in here every trial
            tR = VisionBehaviorTrialRecord()
            # just assign relevant details here
            tR.trialNumber = cR.trialNumber[-1] + 1
            tR.sessionNumber = self.session.sessionNumber
            tR.stationID = self.stationID
            tR.stationName = self.stationName
            tR.numPortsInStation = self.numPorts()
            tR.startTime = time.localtime()
            tR.subjectsInStation = self.subjectsInStation()
            # doTrial - only tR will be returned as its type will be changed
            tR = self.session.subject.do_trial(station=self, trialRecord=tR,
                compiledRecord=cR, quit=Quit)

            tR.stopTime = time.localtime()
            # update sessionRecord and compiledRecord
            sR.append(tR)
            cR.append(tR)


class SimpleVisionBehaviorStation(object):

    def __init__(self):
        print('Creating SimpleVisionBehaviorStation')

    def test_gl(self):
        pygame.init()
        size = width, height = 600, 400
        screen = pygame.display.set_mode(size)
        splashTex = pygame.image.load(os.path.join(
            get_base_directory(), 'BCore', 'Util', 'Resources', 'splash.png'))
        screen.blit(splashTex, [0, 0])
        pygame.display.flip()
        time.sleep(1)

if __name__ == '__main__':
    import sys
    print((sys.version))
    # Create a new StandardVisionBehaviorStation and test it
    #st = StandardVisionBehaviorStation(stationID=0,
    #    display=None, soundOn=False, parallelPort=None)
    st = SimpleVisionBehaviorStation()
    print(('Testing the station\'s graphics'))
    st.test_gl()
    time.sleep(2)