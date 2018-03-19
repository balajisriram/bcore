import time
import os
import psychopy

from ..Hardware.Displays import StandardDisplay
from ..Hardware.Ports import StandardParallelPort
from ... import get_base_directory, get_ip_addr
from uuid import getnode
from verlib import NormalizedVersion as Ver


PPORT_LO = 0
PPORT_HI = 1

class Station(object):
    """
        STATION contains all the relevant details and interfaces to run
        trials from a particular station. This is an abstract class.
        Do not instantiate.
        stationID       : numeric ID
        stationPath     : string path to data storage location
        MACAddress      : unique mac address for the processor/ethernet
                          card. string identifier
    """
    version = Ver('0.0.1')
    station_id = 0
    station_name = ''
    station_path = ''
    station_location = []
    mac_address = ''
    ip_address = ''
    port = 0

    def __init__(self, station_id= 0, station_name='Station0', station_location=(0,0,0)):
        """ Use Station as an abstract class - do not allow setting of
        anything except the basic details"""
        self.station_id = station_id
        self.station_name = station_name
        self.station_path = os.path.join(
            get_base_directory(), 'BStationData', 'StationData',
            str(self.station_id))
        self.station_location = station_location

        self._setup_paths()
        self.mac_address = getnode()
        self.ip_address = get_ip_addr()
        self.port = 5005  # standard for all stations.

    def register(self):
        #
        pass

    def get_subject(self):
        raise NotImplementedError()

    def _setup_paths(self):
        if not os.path.isdir(self.station_path):
            os.makedirs(self.station_path)

    def load(self):
        pass

    def save(self):
        pass

    def load_station(self):
        pass

    def save_station(self):
        pass

    def do_trials(self, **kwargs):
        raise NotImplementedError('Run doTrials() on a subclass')

class StandardVisionBehaviorStation(Station):
    """
        STANDARDVISIONBEHAVIORSTATION(SVBS) defines a subclass of STATION.
        It defines a station with a standard display, a parallel port for i/o
        with standard pin-out settings, sounds settings which can only be
        turned on or off, three valve pins, three sensor pins
        Attributes allowed are:
            station_id       : numeric ID to be sent to STATION
            station_path     : DO NOT SEND - STATION WILL SET IT
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

    def __init__(self,
                 sound_on=False,
                 station_id= 0,
                 station_location=(0,0,0),
                 pport_addr=0xD010,
                 parallel_port='standardVisionBehaviorDefault'):
        super(StandardVisionBehaviorStation, self).__init__(station_id=station_id, station_name=station_name,
                                                          station_location=station_location)
        self.station_id = station_id
        self.station_name = "Station" + str(station_id)
        self.sound_on = sound_on
        self.parallel_port_conn = StandardParallelPort(pport_addr=pport_addr)
        self.parallel_port = parallel_port
        self._window = None
        self._session = None
        self._server_conn = None
        self.display = None
        self._subject = None
        pPort = self.initialize_parallel_port()
        if pPort:
            self.parallel_port = pPort
            self.close_all_valves()
        else:
            self.parallel_port = None

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
        self.splash()
        self.connect_to_server()
        run_trials = False
        while True:
            # look for data from server
            msg = self.get_server_msg()
            quit = False
            if run_trials and ~quit:
                # get info anout session
                self.get_session()

                sub = self._session['subject']
                tR = self._session['trial_record']
                cR = self._session['compiled_record']
                prot = self._session['protocol']
                trial_num = self._session['trial_num']

    def initialize_display(self, display = StandardDisplay()):
        self._window = psychopy.visual.window(display = display,
                                              color = (0,0,0),
                                              fullscr = True,
                                              winType = 'pyglet',
                                              allowGUI = False,
                                              units = 'deg',
                                              screen = 0,
                                              viewScale = None,
                                              waitBlanking = True,
                                              allowStencil = True,
                                              )
        self._window.flip()

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
        self.server_connection = TCPServerConnection(ipaddr=self.ip_address,
            port=self.port)
        self.server_connection.start()
        server_connection_details = self.server_connection.recvData()
        # use server_connection_details to connect to the BServer as a client
        print('Closing connection as server...')
        self.server_connection.stop()
        self.server_connection = BehaviorClientConnection(
            ipaddr=server_connection_details['ipaddr'],
            port=server_connection_details['port'])
        print(('Starting connection as client...'))
        self.server_connection.start()

    def get_subject(self):
        """
            For STANDARDVISIONBEHAVIORSTATION.GETSUBJECT(), get data from
            BServer
        """
        raise NotImplementedError()

    def add_subject(self, sub):
        self._subject = sub

    def remove_subject(self):
        self._subject = None

    def close_all_valves(self):
        self.parallel_port_conn.write_pins(
            self.parallel_port['valvePins'], PPORT_LO)

    def read_ports(self):
        return self.parallel_port_conn.read_pins(
            self.parallel_port['portPins'])

    def open_valve(self, valve):
        self.parallel_port_conn.write_pins(
            self.parallel_port[valve], PPORT_HI)

    def close_valve(self, valve):
        self.parallel_port_conn.write_pins(
            self.parallel_port[valve], PPORT_LO)

    def flush_valves(self, dur=1):
        self.parallel_port_conn.write_pins(
            self.parallel_port['valvePins'], PPORT_HI)
        time.sleep(dur)
        self.parallel_port_conn.write_pins(
            self.parallel_port['valvePins'], PPORT_LO)

    def get_display_size(self):
        pass

    def get_session(self):
        """
            Connect to BServer and request session details to be loaded
        """
        self._session = self._server_conn.client_to_server(self._server_conn.SESSION_REQUESTED)

    def get_compiled_records(self):
        """
            Connect to BServer and request compiledRecords
        """
        return None

    def decache(self):
        """
            Remove session specific details. ideal for pickling
        """
        self._window = None
        self._session = None
        self._server_conn = None
        self._parallelport_conn = None

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

class StandardLocalVisionBehaviorStation(StandardVisionBehaviorStation):
    """
        STANDARDLOCALVISIONBEHAVIORSTATION(SVBS) defines a subclass of
        STANDARDVISIONBEHAVIORSTATION.
        It defines a station with a standard display, a parallel port for i/o
        with standard pin-out settings, sounds settings which can only be
        turned on or off, three valve pins, three sensor pins but also forces
        local server settings

        It achieves this by overwriting get_session(), get_compiled_records(),
        get_subject()
        to be local only by unpickling data from well established locations.
        Ideally used by stand_alone_run()
    """
    display = None

    def __init__(self,
                 sound_on=False,
                 station_id= 0,
                 station_location=(0,0,0),
                 pport_addr=0xD010,
                 parallel_port='standardVisionBehaviorDefault'):
        super(StandardLocalVisionBehaviorStation, self).__init__(sound_on = sound_on,
                                                                 station_id = station_id,
                                                                 station_location = station_location,
                                                                 pport_addr = pport_addr,
                                                                 parallel_port=parallel_port)
        self.station_id = station_id
        self.station_name = "Station" + str(station_id)
        self.sound_on = sound_on
        self.parallel_port_conn = StandardParallelPort(pport_addr=pport_addr)
        self.parallel_port = parallel_port
        self._window = None
        self._session = None
        self._server_conn = None
        pPort = self.initialize_parallel_port()
        if pPort:
            self.parallel_port = pPort
            self.close_all_valves()
        else:
            self.parallel_port = None

    def run(self):
        self.splash()
        self.connect_to_server()
        run_trials = False
        while True:
            # look for data from server
            msg = self.get_server_msg()
            quit = False
            if run_trials and ~quit:
                # get info anout session
                self.get_session()

                sub = self._session['subject']
                tR = self._session['trial_record']
                cR = self._session['compiled_record']
                prot = self._session['protocol']
                trial_num = self._session['trial_num']

    def get_subject(self):
        """
            For STANDARDVISIONBEHAVIORSTATION.GETSUBJECT(), get data from
            BServer
        """
        raise NotImplementedError()

    def get_session(self):
        """
            Connect to BServer and request session details to be loaded
        """
        self._session = self._server_conn.client_to_server(self._server_conn.SESSION_REQUESTED)

    def get_compiled_records(self):
        """
            Connect to BServer and request compiledRecords
        """
        return None

    def decache(self):
        """
            Remove session specific details. ideal for pickling
        """
        self._window = None
        self._session = None
        self._server_conn = None
        self._parallelport_conn = None

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

def make_standard_behavior_station():


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