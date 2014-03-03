import socket
import cPickle
import time

from BCore.Util.parallel.parallelppdev import Parallel


class StandardParallelPort(Parallel):
    """
        STANDARD0PARALLELPORT is a wrapper around parallel.Parallel and is
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

    def __init__(pPort, **kwargs):
        super(StandardParallelPort, pPort).__init__(port=kwargs['pPortAddr'])

    def writePins(pPort, pins, val):
        """
            STANDARDPARALLELPORT.WRITEPINS(PPORT,PINS,VAL)
            call writePin sequentially
        """
        for pin in pins:
            pPort.writePin(pin, val)

    def readPins(pPort, pins):
        """
            STANDARDPARALLELPORT.READPINS(PPORT,PINS)
            call readPin sequentially
        """
        retVal = []
        for pin in pins:
            retVal.append(pPort.readPin(pin))
        return retVal

    def writePin(pPort, pin, state):
        """
            STANDARDPARALLELPORT.WRITEPIN(PIN,VAL)
            Get the data for each pin and only change the data for the pins
            that need to be written
        """
        if state:
            pPort.setData(pPort.PPRDATA() | (2 ** (pin - 2)))
            # pin 2 is the 0th bit in the data sream
        else:
            pPort.setData(pPort.PPRDATA() & (255 ^ 2 ** (pin - 2)))

    def readData(pPort):
        """Return the value currently set on the data pins (2-9)"""
        return (pPort.PPRDATA())

    def readPin(pPort, pin):
        """
            STANDARDPARALLELPORT.READPIN(PIN)
            only certain pins are readable
        """
        if pin == 10:
            return pPort.getInAcknowledge()
        elif pin == 11:
            return pPort.getInBusy()
        elif pin == 12:
            return pPort.getInPaperOut()
        elif pin == 13:
            return pPort.getInSelected()
        elif pin == 15:
            return pPort.getInError()
        elif pin >= 2 and pin <= 9:
            return (pPort.PPRDATA() >> (pin - 2)) & 1
        else:
            print (('Pin %i cannot be read (by PParallelLinux.readPin() yet)'
            % (pin)))


class TCPConnection(object):
    """
        TCPCONNECTION defines a class that determines the read/write protocol
        for data streamed through its channels. It cannot be used directly
        because it cannot be started directly. This works because the only
        difference between server and client is the way connections are started
    """
    TCP_IP = ''
    TCP_PORT = 0
    DEFAULT_BUFFER_SIZE = 0

    def __init__(conn, **kwargs):

        if not kwargs:
            conn.TCP_IP = '127.0.0.1'
            conn.TCP_PORT = 5005
        else:
            conn.TCP_IP = kwargs['ipaddr']
            conn.TCP_PORT = kwargs['port']
        conn.DEFAULT_BUFFER_SIZE = 1024

    def start(conn):
        raise NotImplementedError('TCPConnection needs to be started as a \
            server or as a client. Look at TCPServerConnection and \
            TCPClientConnection')

    def close(conn):
        conn.connection.close()

    def __del__(conn):
        print(('Closing connection...'))
        conn.connection.close()
        print(('done.'))

    def recvData(conn):
        """
            Enforces a max conn.DEFAULT_BUFFER_SIZE message from the client.
            Assumes that the data sent is cPickled at the client end.
        """
        while True:
            BITSTR = conn.connection.recv(conn.DEFAULT_BUFFER_SIZE)
            if not BITSTR:
                break
        return cPickle.loads(BITSTR)

    def sendData(conn, DATA):
        """
            Pickles and sends the data through the socket connection.
        """
        conn.connection.sendall(cPickle.dumps(DATA))


class TCPServerConnection(TCPConnection):
    """
        TCPSERVERCONNECTION subclasses TCP connection. Only difference is in
        the initiation of the connection. As a server, conn.TCP_IP and
        conn.TCP_PORT are bound to the socket and listened to until connection
        is established.

        One extra attribute is defined:
            conn.clientIP           :               IP address of client
    """

    def __init__(conn, **kwargs):
        super(TCPServerConnection, conn).__init__(**kwargs)

    def start(conn):
        conn.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connection.bind((conn.TCP_IP, conn.TCP_PORT))
        print(('Binding socket connection to given IP::port'))
        conn.connection.listen(True)

        print(('Accepting connections at %s::%04d' %
            (conn.TCP_IP, conn.TCP_PORT)))

        (conn.connection, conn.clientIP) = conn.connection.accept()

        print(('Connected to destination at %s' % conn.serverIP))


class TCPClientConnection(TCPConnection):
    """
        TCPCLIENTCONNECTION subclasses TCP connection. Only difference is in
        the initiation of the connection. As a client, conn.TCP_IP and
        conn.TCP_PORT is the location of the server. conn.start() performs
        a socket.connect() until a connection is established
    """

    def __init__(conn, **kwargs):
        super(TCPServerConnection, conn).__init__(**kwargs)

    def start(conn):
        conn.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(('Connecting to server at %s::%s...' % (
            (conn.TCP_IP, conn.TCP_PORT))))
        Connected = False
        while not Connected:
            try:
                conn.connection.connect((conn.TCP_IP, conn.TCP_PORT))
                Connected = True
            except socket.error:
                print(('Server busy...retrying ...'))
                time.sleep(1)
        print(('Connected.'))


class BehaviorServerConnection(TCPServerConnection):
    """
        BEHAVIORSERVERCONNECTION makes the BServer act as a server. Special
        constants are defined for communication with the client along with 
        acknowledgement codes that allow the server to continue its function.
        
        It is important to keep the constants defined here in sync with the 
        constants defined in BEHAVIORCLIENTCONNECTION. 
    """
    # client side commands to server
    COMMAND_REQUESTED = 0 # in station loop, ask for things to do 
    SUBJECT_REQUESTED = 0 # in station.run() request subject details
    TRIALRECORDS_REQUESTED = 0 # in station.run() request trialRecords
    KILL_REQUEST = 0 # something is terribly wrong and i am going to kill
    
    ACCEPT_TRIALRECORDS = 0 # cleanly killing station needs to send trialRecs
    
    # server side commands to client
    ACK_NONE = 65535 # if receive  ACK_NONE keep on looping
    ACK_SUBJECT = 65535 # acknowledgement for receipt for subject
    ACK_KILL = 65535 # acknowledge going into kill mode

class BehaviorClientConnection(TCPClientConnection):
    """
        BEHAVIORCLIENTCONNECTION makes the station act as a client. Special
        constants are defined for communication with the server along with 
        acknowledgement codes that allow the server to continue its function.
        
        It is important to keep the constants defined here in sync with the 
        constants defined in BEHAVIORSERVERCONNECTION. 
    """
    
    # client side commands to server
    REQUEST_COMMAND = 0 # in station loop, ask for things to do 
    REQUEST_SUBJECT = 0 # in station.run() request subject details
    REQUEST_TRIALRECORDS = 0 # in station.run() request trialRecords
    REQUEST_KILL = 0 # something is terribly wrong and i am going to kill
    
    ACCEPT_TRIALRECORDS = 0 # cleanly killing station needs to send trialRecs
    
    # server side commands to client
    ACK_NONE = 65535 # if receive  ACK_NONE keep on looping
    ACK_SUBJECT = 65535 # acknowledgement for receipt for subject
    ACK_KILL = 65535 # acknowledge going into kill mode
    
    def __init__(conn, **kwargs):
        super(BehaviorClientConnection, conn).__init__(**kwargs)
