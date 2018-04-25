import time
import zmq

from ...Util.parallel.parallelppdev import Parallel

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class StandardParallelPort(Parallel):
    """
        STANDARDPARALLELPORT is a wrapper around parallel.Parallel and is
        specifically used to read and write multiple pins simultaneously.
        For use cases, see StandardParallelPort.writePins() and
        StandardParallelPort.readPins()

        Pin Out for a Standard Parallel Port
        Pin No    Signal name    Direction    Register-bit        Inverted
        1         nStrobe            Out        Control-0           Yes
        2         Data0            In/Out        Data-0             No
        3         Data1            In/Out        Data-1             No
        4         Data2            In/Out        Data-2             No
        5         Data3            In/Out        Data-3             No
        6         Data4            In/Out        Data-4             No
        7         Data5            In/Out        Data-5             No
        8         Data6            In/Out        Data-6             No
        9         Data7            In/Out        Data-7             No
        10        InAck              In         Status-6            No
        11        Busy               In         Status-7            Yes
        12        Paper-Out          In         Status-5            No
        13        Select             In         Status-4            No
        14        Linefeed           Out        Control-1           Yes
        15        nError             In         Status-3            No
        16        nInitialize        Out        Control-2           No
        17        nSelect-Printer    Out        Control-3           Yes
        18-25     Ground              -            -                -

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
    """

    def __init__(self, **kwargs):
        super(StandardParallelPort, self).__init__(port=kwargs['pPortAddr'])

    def write_pins(self, pins, val):
        """
            STANDARDPARALLELPORT.WRITEPINS(PPORT,PINS,VAL)
            call writePin sequentially
        """
        for pin in pins:
            self.write_pin(pin, val)

    def read_pins(self, pins):
        """
            STANDARDPARALLELPORT.READPINS(PPORT,PINS)
            call readPin sequentially
        """
        retVal = []
        for pin in pins:
            retVal.append(self.read_pin(pin))
        return retVal

    def write_pin(self, pin, state):
        """
            STANDARDPARALLELPORT.WRITEPIN(PIN,VAL)
            Get the data for each pin and only change the data for the pins
            that need to be written
        """
        if state:
            self.setData(self.PPRDATA() | (2 ** (pin - 2)))
            # pin 2 is the 0th bit in the data sream
        else:
            self.setData(self.PPRDATA() & (255 ^ 2 ** (pin - 2)))

    def read_data(self):
        """Return the value currently set on the data pins (2-9)"""
        return (self.PPRDATA())

    def read_pin(self, pin):
        """
            STANDARDPARALLELPORT.READPIN(PIN)
            only certain pins are readable
        """
        if pin == 10:
            return self.getInAcknowledge()
        elif pin == 11:
            return self.getInBusy()
        elif pin == 12:
            return self.getInPaperOut()
        elif pin == 13:
            return self.getInSelected()
        elif pin == 15:
            return self.getInError()
        elif pin >= 2 and pin <= 9:
            return (self.PPRDATA() >> (pin - 2)) & 1
        else:
            print (('Pin %i cannot be read (by PParallelLinux.readPin() yet)'
            % (pin)))


class ServerMessage(object):
    """
        SERVERMESSAGE is a class that will contain information about messages
        sent by the Server. Server can send multiple types of messages to the
        clients
        1. Initiate session (includes subject, protocol ...)
        2. Kill Session (request information about session - records, num trials ...)
        3.

        It is important to keep the constants defined here in sync with the
        constants defined in CLIENTMESSAGE.
    """

    # client side commands to server
    COMMAND_REQUESTED = 0  # in station loop, ask for things to do
    SUBJECT_REQUESTED = 0  # in station.run() request subject details
    TRIALRECORDS_REQUESTED = 0  # in station.run() request trialRecords
    KILL_REQUEST = 0  # something is terribly wrong and i am going to kill

    ACCEPT_TRIALRECORDS = 0  # cleanly killing station needs to send trialRecs

    # server side commands to client
    ACK_NONE = 65535  # if receive  ACK_NONE keep on looping
    ACK_SUBJECT = 65535  # acknowledgement for receipt for subject
    ACK_KILL = 65535  # acknowledge going into kill mode


class ClientMessage(object):
    """
        CLIENTMESSAGE makes the station act as a client. Special
        constants are defined for communication with the server along with
        acknowledgement codes that allow the server to continue its function.

        It is important to keep the constants defined here in sync with the
        constants defined in SERVERMESSAGE.
    """

    # client side commands to server
    REQUEST_COMMAND = 0  # in station loop, ask for things to do
    REQUEST_SUBJECT = 0  # in station.run() request subject details
    REQUEST_TRIALRECORDS = 0  # in station.run() request trialRecords
    REQUEST_KILL = 0  # something is terribly wrong and i am going to kill

    ACCEPT_TRIALRECORDS = 0  # cleanly killing station needs to send trialRecs

    # server side commands to client
    ACK_NONE = 65535  # if receive  ACK_NONE keep on looping
    ACK_SUBJECT = 65535  # acknowledgement for receipt for subject
    ACK_KILL = 65535  # acknowledge going into kill mode

    def __init__(conn, **kwargs):
        super(BehaviorClientConnection, conn).__init__(**kwargs)
