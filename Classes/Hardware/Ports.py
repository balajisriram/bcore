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
            pPort.setData(pPort.port.PPRDATA() | (2 ** (pin - 2)))
            # pin 2 is the 0th bit in the data sream
        else:
            pPort.setData(pPort.port.PPRDATA() & (255 ^ 2 ** (pin - 2)))

    def readData(self):
        """Return the value currently set on the data pins (2-9)"""
        return (self.port.PPRDATA())

    def readPin(self, pin):
        """
            STANDARDPARALLELPORT.READPIN(PIN)
            only certain pins are readable
        """
        if pin == 10:
            return self.port.getInAcknowledge()
        elif pin == 11:
            return self.port.getInBusy()
        elif pin == 12:
            return self.port.getInPaperOut()
        elif pin == 13:
            return self.port.getInSelected()
        elif pin == 15:
            return self.port.getInError()
        elif pin >= 2 and pin <= 9:
            return (self.port.PPRDATA() >> (pin - 2)) & 1
        else:
            print (('Pin %i cannot be read (by PParallelLinux.readPin() yet)'
            % (pin)))
