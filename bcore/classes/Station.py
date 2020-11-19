import os
import psychopy
from psychopy import event
import psychopy.logging
import psychopy.parallel
import psychopy.visual
import json
psychopy.logging.console.setLevel(psychopy.logging.WARNING)
import numpy as np

from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']

import psychopy.sound
import bcore.classes.Hardware.Displays as displays
from bcore import get_base_path, get_config_path, DATETIME_TO_STR
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

def compile_records(compiled_record, trial_record):
    regular_fields = ["session_number",
    "trial_number",
    "station_id",
    "num_ports_in_station",
    "trial_start_time",
    "trial_stop_time",
    "subject_id",
    "current_step",
    "num_steps",
    "criterion_met",
    "graduate",
    "errored_out",
    "manual_quit",
    "correct"]
    lut_fields = ["station_name",
    "station_version_number",
    "subject_version_number",
    "protocol_name",
    "protocol_version_number",
    "current_step_name",
    "trial_manager_name",
    "session_manager_name",
    "criterion_name",
    "reinforcement_manager_name",
    "trial_manager_class",
    "session_manager_class",
    "criterion_class",
    "reinforcement_manager_class",
    "trial_manager_version_number",
    "session_manager_version_number",
    "criterion_version_number",
    "reinforcement_manager_version_number",]
    LUT = compiled_record['LUT']
    num_trials = len(compiled_record['trial_number'])
    for field in regular_fields:
        try:
            value = trial_record[field]
        except KeyError:
            value = None
        if not field in compiled_record: compiled_record[field] = [None for i in range(0,num_trials)] # None padding
        compiled_record[field].append(value)

    for field in lut_fields:
        try:
            value = trial_record[field]
        except KeyError:
            value = 'NotAvailable'
        idx,LUT = add_or_find_in_LUT(LUT,value)
        if not field in compiled_record: compiled_record[field] = [None for i in range(0,num_trials)] # None padding
        compiled_record[field].append(idx)
    compiled_record['LUT'] = LUT

    try:
        trial_specific_compiler = trial_record['trial_compiler']
        compiled_record = trial_specific_compiler(compiled_record,trial_record)
    except KeyError as e:
        print('No trial specific compiler. Ignoring trial')

    return compiled_record


def get_mac_address():
    configuration = json.config(os.path.join(get_config_path(),'bcore.config'))
    return configuration['mac_addr']

def get_ip_address():
    configuration = json.config(os.path.join(get_config_path(),'bcore.config'))
    return configuration['ip_addr']

def get_port():
    configuration = json.config(os.path.join(get_config_path(),'bcore.config'))
    return configuration['ip_port']

####################################################################
####################### CLASSES FOR STATIONS #######################
####################################################################
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
    _subject = None
    _key_pressed = []
    _sounds = {}
    _stims = {}
    _clocks = {}
    _parallel_port_conn = None
    creation_time = ''
    station_version = Ver('0.0.1')
    station_id = None
    station_name = ''
    station_path = ''
    station_location = None


    def __init__(self, **kwargs):
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self, data):
        self.station_version = Ver(data['station_version'])
        self.creation_time = datetime.datetime.strptime(data['creation_time'],DATETIME_TO_STR)
        self.station_id = data['station_id']
        self.station_name = data['station_name']
        self.station_path = data['station_path']
        self.station_location = data['station_location']
        self.mac_address = data['mac_address']
        self.ip_address = data['ip_address']
        self.port = data['port']
        return self

    def save_to_dict(self):
        data = dict()
        data['station_version'] = self.station_version.__str__()
        data['station_id'] = self.station_id
        data['station_name'] = self.station_name
        data['station_path'] = self.station_path
        data['station_location'] = self.station_location
        data['creation_time'] = datetime.datetime.strftime(self.creation_time,DATETIME_TO_STR)
        data['mac_address'] = self.mac_address
        data['ip_address'] = self.ip_address
        data['port'] = self.port
        return data

    def __repr__(self):
        return "Station object with id:%s, location:%s and ip:%s" %(self.station_id, self.station_location, self.ip_address)

    def register(self):
        #
        pass

    def _setup_paths(self):
        if not os.path.isdir(self.station_path):
            os.makedirs(self.station_path)

    def do_trials(self, **kwargs):
        raise NotImplementedError('Run doTrials() on a subclass')

    def initialize_sounds(self):
        self._sounds['trial_start_sound'] = psychopy.sound.Sound(440,stereo=0,secs=1.,hamming=True)

        self._sounds['request_sound'] = psychopy.sound.Sound(493.88,stereo=0,secs=1.,hamming=True)
        self._sounds['stim_start_sound'] = psychopy.sound.Sound(493.88,stereo=0,secs=1.,hamming=True)
        self._sounds['go_sound'] = psychopy.sound.Sound(493.88,stereo=0,secs=1.,hamming=True)
        self._sounds['keep_going_sound'] = psychopy.sound.Sound(493.88,stereo=0,secs=1.,hamming=True)
        self._sounds['request_sound'] = psychopy.sound.Sound(493.88,stereo=0,secs=1.,hamming=True)

        self._sounds['correct_sound'] = psychopy.sound.Sound(523.25,stereo=0,secs=1.,hamming=True)
        self._sounds['reward_sound'] = psychopy.sound.Sound(523.25,stereo=0,secs=1.,hamming=True)
        self._sounds['trial_end_sound'] = psychopy.sound.Sound(523.25,stereo=0,secs=1.,hamming=True)

        sampleRate,secs,f_punishment=(44100,2,[370,440])
        nSamples = int(secs * sampleRate)
        phase = 2*np.pi*np.linspace(0.0, 1.0, nSamples)
        val = np.full_like(phase,0.)
        for f in f_punishment:
            val += np.sin(f*phase)
        val = np.matlib.repmat(val,2,1)
        self._sounds['punishment_sound'] = psychopy.sound.Sound(val.T,hamming=True)

        val = 0.5*np.random.randn(1,nSamples)
        val = np.matlib.repmat(val,2,1)
        self._sounds['try_something_else'] = psychopy.sound.Sound(val.T,hamming=True)


        self._sounds['trial_end_sound'] = psychopy.sound.Sound(587.33,stereo=0,secs=1.,hamming=True)

    def _rewind_sounds(self,time=0.):
        for sound in self._sounds:
            self._sounds[sound].seek(time)

    def decache(self):
        """
            Remove session specific details. ideal for pickling
        """
        self._key_pressed = None
        self._sounds = None
        self._stims = None
        self._clocks = None


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
    _window = None
    _session = None
    _server_conn = None

    svbstation_version = Ver('0.0.1')
    sound_on = False
    io_type = ''
    parallel_port = None
    parallel_port_address = ''
    display_name = ''
    display_type = ''
    display = None


    def __init__(self,**kwargs):
        super(StandardVisionBehaviorStation, self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data]'])
        else:
            pass
        self.display = self.get_display()
        self.parallel_port = self.get_parport_mappings()

    def load_from_dict(self,data):
        self.svbstation_version = Ver(data['svbstation_version'])
        self.sound_on = data['sound_on']
        self.io_type = data['io_type']
        self.parallel_port = data['parallel_port']
        self.parallel_port_address = data['parallel_port_address']
        self.display_name = data['display_name']
        self.display_type = data['display_type']
        return self

    def save_to_dict(self):
        data = super(StandardVisionBehaviorStation,self).save_to_dict()
        data['svbstation_version'] = self.svbstation_version
        data['sound_on'] = self.sound_on
        data['io_type'] = self.io_type
        data['parallel_port'] = self.parallel_port
        data['parallel_port_address'] = self.parallel_port_address
        data['display_name'] = self.display_name
        data['display_type'] = self.display_type
        return data

    def __repr__(self):
        return "StandardVisionBehaviorStation object with id:%s, location:%s and ip:%s" %(self.station_id, self.station_location, self.ip_address)

    def get_display(self):
        return displays.StandardDisplay()

    def get_parport_mappings(self):
        if self.parallel_port == 'standardVisionBehaviorDefault':
            print('STANDARDVISIONBEHAVIORSTATION:INITIALIZE_PARALLEL_PORT::setting parallelport to standardVisionBehaviorDefault')
            pPort = {}
            pPort['right_valve'] = 2
            pPort['center_valve'] = 3
            pPort['left_valve'] = 4
            pPort['valve_pins'] = [2, 3, 4]
            pPort['center_port'] = 10
            pPort['right_port'] = 12
            pPort['left_port'] = 13
            pPort['port_pins'] = [13, 10, 12]
            pPort['index_pin'] = 8
            pPort['frame_pin'] = 9
            pPort['trial_pin'] = 6
            pPort['led_0'] = 5
            pPort['led_1'] = 7
            return pPort
        elif self.parallel_port == 'standardHeadfixBehaviorDefault':
            print('STANDARDVISIONBEHAVIORSTATION:INITIALIZE_PARALLEL_PORT::setting parallelport to standardVisionHeadfixDefault')
            pPort = {}
            pPort['reward_valve'] = 3
            pPort['valve_pins'] = [3,]
            pPort['response_port'] = 10
            pPort['running_port'] = 13
            pPort['port_pins'] = [10,]
            pPort['index_pin'] = 8
            pPort['frame_pin'] = 9
            pPort['trial_pin'] = 6
            pPort['led_0'] = 5
            pPort['led_1'] = 7
            return pPort
        else:
            return None # need to write code that checks if allowable

    def initialize(self):
        self.initialize_display(display=self.display)
        self.initialize_sounds()
        self.initialize_parallel_port()
        self.close_all_valves()

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

    def initialize_display(self, display = displays.StandardDisplay()):
        self._window = psychopy.visual.Window(color=(0.,0.,0.), fullscr=True, winType='pyglet', allowGUI=False, units='deg', screen=0, viewScale=None, waitBlanking=True, allowStencil=True,monitor = display)
        self._window.flip()

    def initialize_parallel_port(self):
        self._parallel_port_conn = psychopy.parallel.ParallelPort(address=self.parallel_port_address)
        self.close_all_valves()

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
        print('STANDARDVISIONBEHAVIORSTATION:CONNECT_TO_SERVER::Closing connection as server...')
        self._server_conn.stop()
        self._server_conn = BehaviorClientConnection(
            ipaddr=server_connection_details['ipaddr'],
            port=server_connection_details['port'])
        print('STANDARDVISIONBEHAVIORSTATION:CONNECT_TO_SERVER::Starting connection as client...')
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
    def session(self,value):
        self._session = value

    def get_ports(self):
        return np.asarray(['left_port','center_port','right_port'])

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
        val = list('{0:08b}'.format(self._parallel_port_conn.readData()))
        for valve in self.parallel_port['valve_pins']:
            val[1-valve] = '0'
        self._parallel_port_conn.setData(int(''.join(val),2))

    def read_ports(self):
        out = [False, False, False]
        port_names = ['left_port','center_port','right_port']
        for i,port in enumerate(self.parallel_port['port_pins']):
            out[i] = self._parallel_port_conn.readPin(port)
        active_ports = [x for x,y in zip(port_names,out) if not y]
        return active_ports

    def open_valve(self, valve):
        valve_pin = self.parallel_port[valve]
        self.set_pin_on(valve_pin)

    def close_valve(self, valve):
        valve_pin = self.parallel_port[valve]
        self.set_pin_off(valve_pin)

    def flush_valves(self, dur=1):
        val = list('{0:08b}'.format(self._parallel_port_conn.readData()))
        for valve in self.parallel_port['valve_pins']:
            val[1-valve] = '1'
        self._parallel_port_conn.setData(int(''.join(val),2))

        time.sleep(dur)

        for valve in self.parallel_port['valve_pins']:
            val[1-valve] = '0'
        self._parallel_port_conn.setData(int(''.join(val),2))

    def set_index_pin_on(self):
        index_pin = self.parallel_port['index_pin']
        self.set_pin_on(index_pin)

    def set_index_pin_off(self):
        index_pin = self.parallel_port['index_pin']
        self.set_pin_off(index_pin)

    def set_frame_pin_on(self):
        frame_pin = self.parallel_port['frame_pin']
        self.set_pin_on(frame_pin)

    def set_frame_pin_off(self):
        frame_pin = self.parallel_port['frame_pin']
        self.set_pin_off(frame_pin)

    def set_trial_pin_on(self):
        trial_pin = self.parallel_port['trial_pin']
        self.set_pin_on(trial_pin)

    def set_trial_pin_off(self):
        trial_pin = self.parallel_port['trial_pin']
        self.set_pin_off(trial_pin)

    def set_pin_on(self,pin):
        if pin<2 or pin>9:
            ValueError('Cannot deal with this')
        val = list('{0:08b}'.format(self._parallel_port_conn.readData()))
        val[1-pin] = '1'
        self._parallel_port_conn.setData(int(''.join(val),2))

    def set_pin_off(self,pin):
        if pin<2 or pin>9:
            ValueError('Cannot deal with this')
        val = list('{0:08b}'.format(self._parallel_port_conn.readData()))
        val[1-pin] = '0'
        self._parallel_port_conn.setData(int(''.join(val),2))

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
        self._parallel_port_conn = None
        self._clocks = None

    def do_trials(self, **kwargs):
        # first step in the running of trials. called directly by station
        # or through the BServer
        if __debug__:
            pass
        self.initialize()
        # get the compiled_records for the animal. Compiled records will contain all the information that will be used in
        # the course of running the experiment. If some stimulus parameter for a given trial is dependent on something in
        # the previous trial, please add it to compiled records
        compiled_record = self.subject.load_compiled_records()
        quit = False

        # session starts here
        session_record = []  # just a list of tRs
        session_number = compiled_record["session_number"][-1] + 1

        # setup the clocks
        self._clocks['session_clock'] = psychopy.core.MonotonicClock()
        self._clocks['trial_clock'] = psychopy.core.Clock()
        session_start_time = psychopy.core.getAbsTime()

        while not quit:
            # it loops in here every trial
            trial_record = {}
            # just assign relevant details here
            trial_record["session_start_time"] = session_start_time
            trial_record["trial_number"] = compiled_record["trial_number"][-1] + 1
            trial_record["session_number"] = session_number
            trial_record["station_id"] = self.station_id
            trial_record["station_version_number"] = self.ver.__str__()
            trial_record["station_name"]= self.station_name
            trial_record["num_ports_in_station"] = self.num_ports
            trial_record["trial_start_time"] = self._clocks['session_clock'].getTime()
            # doTrial - only trial_record will be returned as its type will be changed
            trial_record, quit = self.subject.do_trial(station=self, trial_record=trial_record, compiled_record=compiled_record, quit=quit)

            trial_record["trial_stop_time"] = self._clocks['session_clock'].getTime()
            # update sessionRecord and compiledRecord
            compiled_record = compile_records(compiled_record,trial_record)
            session_record.append(trial_record)

        # save session records
        self.subject.save_session_records(session_record)
        # save compiled records
        self.subject.save_compiled_records(compiled_record)

        self.decache()

    def close_session(self, **kwargs):
        print("STANDARDVISIONBEHAVIORSTATION:CLOSE_SESSION::Closing Session")

    def close_window(self):
        self._window.close()

    def check_manual_quit(self):
        key = psychopy.event.getKeys(keyList=['k','q'])
        if key:
            if not key[0] in self._key_pressed: self._key_pressed.append(key[0])
        if 'k' in self._key_pressed and 'q' in self._key_pressed:
            psychopy.event.clearEvents()
            return True
        else:
            return False

    def read_kb(self):
        key,modifier = event.getKeys(keyList=['1','2','3','k'],modifier=True)
        ports = np.asarray([False,False,False])
        if key:
            if not key[0] in self._key_pressed: self._key_pressed.append(key[0])
        if 'k' in self._key_pressed and '1' in self._key_pressed:
            self._key_pressed.remove('k')
            self._key_pressed.remove('1')
        if 'k' in self._key_pressed and '2' in self._key_pressed:
            ports = np.bitwise_or(ports,[False,True,False])
            psychopy.event.clearEvents()
            print(self._key_pressed)
            self._key_pressed.remove('k')
            self._key_pressed.remove('2')
        if 'k' in self._key_pressed and '3' in self._key_pressed:
            ports = np.bitwise_or(ports,[False,False,True])
            psychopy.event.clearEvents()
            print(self._key_pressed)
            self._key_pressed.remove('k')
            self._key_pressed.remove('3')

        return self.get_ports()[ports]

class StandardVisionHeadfixStation(StandardVisionBehaviorStation):
    """
        STANDARDVISIONHEADFIXSTATION(SVHS) defines a subclass of SVBS.
        It defines a station with a standard display, a parallel port for i/o
        with standard pin-out settings, sounds settings which can only be
        turned on or off, one valve pins, one sensor pins. Only allows
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
            Pin 3            :            Center Reward Valve
            Pin 8            :            indexPulse
            Pin 9            :            framePulse
            Pin 10           :            Center Response Sensor
        While, these values are not hard coded here, use these values if you
        want your system to work :)

        Use these defaults unless you know what you are doing
        parallel_port = {}
        parallel_port['center_valve'] = 3
        parallel_port['valve_pins'] = (3)
        parallel_port['center_port'] = 10
        parallel_port['port_pins'] = (10)
        parallel_port['index_pin'] = 8
        parallel_port['frame_pin'] = 9
        parallel_port['led_0'] = 5
        parallel_port['led_1'] = 7
    """

    svhfstation_version = Ver('0.0.1')


    def __init__(self,**kwargs):
        super(StandardVisionHeadfixStation, self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data]'])
        else:
            pass

    def load_from_dict(self,data):
        self.svhfstation_version = Ver(data['svhfstation_version'])
        return self

    def save_to_dict(self):
        data = super(StandardVisionHeadfixStation,self).save_to_dict()
        data['svhfstation_version'] = self.svhfstation_version
        return data

    def __repr__(self):
        return "StandardVisionHeadfixStation object with id:%s, location:%s and ip:%s" %(self.station_id, self.station_location, self.ip_address)

    def get_ports(self):
        return np.asarray(['response_port'])

    def read_ports(self):
        port_names = ['response_port']
        if self._parallel_port_conn.readPin(self.parallel_port['port_pins'][0]):
            return [] # when the lick port is high then it is empty.
        else:
            return ['response_port'] # when the lick port is low, then there is licking

    def open_valve(self, valve):
        valve_pin = self.parallel_port[valve]
        self.set_pin_on(valve_pin)

    def close_valve(self,valve):
        valve_pin = self.parallel_port[valve]
        self.set_pin_off(valve_pin)

    def close_all_valves(self):
        self.close_valve('reward_valve')


class StandardKeyboardStation(StandardVisionBehaviorStation):
    """
        STANDARDKEYBOARDSTATION(SKBS) defines a subclass of
        STANDARDVISIONBEHAVIORSTATION(SVBS).
        It defines a station with a standard display, sounds settings
        which can only be turned on or off, three sensor pins
        [connected to the keyboard]. Only allows stand alone running
        Attributes allowed are:
            station_id       : numeric ID to be sent to STATION
            station_path     : DO NOT SEND - STATION WILL SET IT
            display          : dictionary containing details about the
                               display unit
            soundOn          : True/False

        For the StandardKeyboardStation:
            K+1              :            Left Sensor
            K+2              :            Center Sensor
            K+3              :            Right Sensor
            K+Q              :            Quit

    """

    skstation_version = Ver('0.0.1')


    def __init__(self,**kwargs):
        super(StandardKeyboardStation, self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data]'])
        else:
            pass

    def load_from_dict(self,data):
        self.skstation_version = Ver(data['skstation_version'])
        return self

    def save_to_dict(self):
        data = super(StandardKeyboardStation,self).save_to_dict()
        data['skstation_version'] = self.skstation_version
        return data

    def __repr__(self):
        return "StandardKeyboardStation object with id:%s, location:%s and ip:%s" %(self.station_id, self.station_location, self.ip_address)


    @property
    def num_ports(self):
        return 3

    def read_ports(self):
        key = psychopy.event.getKeys(keyList=['1','2','3','k'])
        ports = np.asarray([False,False,False])
        if key:
            if not key[0] in self._key_pressed: self._key_pressed.append(key[0])
        if 'k' in self._key_pressed and '1' in self._key_pressed:
            ports = np.bitwise_or(ports,[True,False,False])
            psychopy.event.clearEvents()
            print(self._key_pressed)
            self._key_pressed.remove('k')
            self._key_pressed.remove('1')
        if 'k' in self._key_pressed and '2' in self._key_pressed:
            ports = np.bitwise_or(ports,[False,True,False])
            psychopy.event.clearEvents()
            print(self._key_pressed)
            self._key_pressed.remove('k')
            self._key_pressed.remove('2')
        if 'k' in self._key_pressed and '3' in self._key_pressed:
            ports = np.bitwise_or(ports,[False,False,True])
            psychopy.event.clearEvents()
            print(self._key_pressed)
            self._key_pressed.remove('k')
            self._key_pressed.remove('3')

        return self.get_ports()[ports]

    def open_valve(self, valve):
        print('Opening valve',valve)

    def close_valve(self, valve):
        print('Closing valve',valve)

    def flush_valves(self, dur=1):
        pass

    def close_all_valves(self):
        print('Closing all valves')

    def initialize(self):
        self.initialize_display(display=self.display)
        self.initialize_sounds()
        self.close_all_valves()


if __name__ == '__main__':
    from psychopy.constants import (STARTED, PLAYING, PAUSED, FINISHED, STOPPED, NOT_STARTED, FOREVER)
    import psychopy.core
    nSamples = 4410
    val = 0.5*np.random.randn(1,nSamples)+0.5

    # sampleRate,secs,f_punishment=(44100,0.02,[370,440])
    # nSamples = int(secs * sampleRate)
    # phase = 2*np.pi*np.linspace(0.0, 1.0, nSamples)
    # val = np.full_like(phase,0.)
    # for f in f_punishment:
        # val += np.sin(f*phase)
    print(np.min(val))
    print(np.max(val))
    val = np.matlib.repmat(val,2,1)
    punishment_sound = psychopy.sound.Sound(val.T,hamming=True)

    # print(val)

    punishment_sound.play()
    while punishment_sound.status==PLAYING:
        psychopy.core.wait(0.1)
    punishment_sound.stop()
    print(val.shape)
    # import time
    # st = StandardVisionHeadfixStation()
    # st.initialize()
    # rect = psychopy.visual.Rect(st._window, lineColor=None,fillColor=(0.,0.,0.), width=0.5, height=0.5, units='norm')

    # for i in range(256):
        # rect.fillColor=((2*i-255)/255., (2*i-255)/255., (2*i-255)/255.)
        # rect.draw()
        # st.set_pin_on(9)
        # st._window.flip()
        # st.set_pin_off(9)


    # st.close_window()
