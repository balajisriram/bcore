from psychopy import monitors

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

def StandardDisplay():
    return Dell_E3211H()


def Dell_E3211H():
    name = 'Dell_E3211H'
    x_pixels = 1920
    y_pixels = 1080
    x_size = 509.8  # mm
    y_size = 286.7  # mm
    distance_to_subject = 120  # mm
    make = 'Dell'
    model = 'E2311H'

    mon = psychopy.monitors.Monitor(name,
                                    width = 50.98,
                                    distance = 12,
                                    gamma = 1.2)
    return mon