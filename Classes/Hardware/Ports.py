from parallel import Parallel


class ParallelPort(Parallel):
    """
        PARALLELPORT is a wrapper around parallel.Parallel and is specifically
        used to read and write multiple pins simultaneously
    """

    def __init__(pPort, **kwargs):
        super(ParallelPort, pPort).__init__(port=kwargs['pPortAddr'])

    def setPins(pPort, pins, val):
        pass

    def readPins(pPort, pins):
        pass
