import time
import os
import psychopy

from .Hardware.Displays import StandardDisplay
from .. import get_base_directory, get_ip_addr
from uuid import getnode
from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

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
    _subject = None

    def __init__(self, station_id= 0, station_name='Station0', station_location=(0,0,0)):
        """ Use Station as an abstract class - do not allow setting of
        anything except the basic details"""
        self.station_id = station_id
        self.station_name = station_name
        self.station_path = os.path.join(
            get_base_directory(), 'BCoreData', 'BStationData', 'StationData',
            str(self.station_id))
        self.station_location = station_location

        self._setup_paths()
        self.mac_address = getnode()
        self.ip_address = get_ip_addr()
        self.port = 5005  # standard for all stations.

    def register(self):
        #
        pass

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
        turned on or off, three valve pins, three sensor pins. Only allows
        stand alone running
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
    version = Ver('0.0.1')
    _window = None
    _session = None
    _server_conn = None
    _subject = None

    def __init__(self,
                 sound_on=False,
                 station_id= 0,
                 station_location=(0,0,0),
                 pport_addr=0xD010,
                 parallel_port='standardVisionBehaviorDefault'):
        super(StandardVisionBehaviorStation, self).__init__(station_location=station_location)
        self.station_id = station_id
        self.station_name = "Station" + str(station_id)
        self.sound_on = sound_on
        self.parallel_port = parallel_port
        self.display = None
        pPort = self.initialize_parallel_port()
        if pPort:
            from .Hardware.Ports import StandardParallelPort
            self.parallel_port = pPort
            self.parallel_port_conn = StandardParallelPort(pport_addr=pport_addr)
            self.close_all_valves()
        else:
            self.parallel_port = None
            self.parallel_port_conn = None

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
        self._server_conn = TCPServerConnection(ipaddr=self.ip_address,
            port=self.port)
        self._server_conn.start()
        server_connection_details = self._server_conn.recvData()
        # use server_connection_details to connect to the BServer as a client
        print('Closing connection as server...')
        self._server_conn.stop()
        self._server_conn = BehaviorClientConnection(
            ipaddr=server_connection_details['ipaddr'],
            port=server_connection_details['port'])
        print(('Starting connection as client...'))
        self._server_conn.start()

    @property
    def subject(self):
        return self._subject
        
    @subject.setter
    def subject(self,value):
        self._subject = value

    @property
    def session(self):
        return self._session
    
    @session.setter
    def subject(self,value):
        self._session = value
        
    @property
    def num_ports(self):
        if self.parallel_port:
            return len(self.parallel_port['port_pins'])
        else:
            return 0

    def add_subject(self, sub):
        self.subject = sub
            #if sub.subject_id in self.get_subjects():
            #    RuntimeError("STATION:STANDARDVISIONBEHAVIORSTATION:ADD_SUBJECT:Subject "+ sub.subject_id + " already in station. Cannot add twice")
            #
            #print("STATION:STANDARDVISIONBEHAVIORSTATION:ADD_SUBJECT: Adding subject_id " + sub.subject_id +" to station_id " + str(self.station_id))
            #self.subjects.append(sub)

    def remove_subject(self,sub):
        self.subject = None
            #if sub.subject_id not in self.get_subjects():
            #    RuntimeError("STATION:STANDARDVISIONBEHAVIORSTATION:ADD_SUBJECT:Subject "+ sub.subject_id + " not in station. Cannot remove.")
            #print("STATION:STANDARDVISIONBEHAVIORSTATION:REMOVE_SUBJECT: Removing subject_id " + sub.subject_id +" from station_id " + str(self.station_id))
            #idx = [i for (i,x) in enumerate(self.get_subjects()) if x==sub.subject_id]
            #self.subjects = self.subjects[:idx[0]]+self.subjects[idx[0]+1:]

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

        # get the compiled_records for the animal. Compiled records will contain all the information that will be used in
        # the course of running the experiment. If some stimulus parameter for a given trial is dependent on something in
        # the previous trial, please add it to compiled records
        cR = self.subject.load_compiled_records()
        Quit = False

        # session starts here
        sR = []  # just a list of tRs

        while not Quit:
            # it loops in here every trial
            tR = {}
            # just assign relevant details here
            tR["trial_number"] = cR[-1]["trial_number"] + 1
            tR["session_number"] = cR[-1]["session_number"] + 1
            tR["station_id"] = self.station_id
            tR["station_name"]= self.station_name
            tR["num_ports_in_station"] = self.num_ports
            tR["start_time"] = time.localtime()
            # doTrial - only tR will be returned as its type will be changed
            tR, quit = self.subject.do_trial(station=self, trial_record=tR, compiled_record=cR, quit=Quit)

            tR["stop_time"] = time.localtime()
            # update sessionRecord and compiledRecord
            cR.append(tR)

        # save session records
        self._subject.save_session_records(sR)
        # save compiled records
        self._subject.save_compiled_records(cR)


def make_standard_behavior_station():
    pass


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
