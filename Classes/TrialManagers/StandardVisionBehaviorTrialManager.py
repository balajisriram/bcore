from .TrialManager import TrialManager
from verlib import NormalizedVersion as Ver

do_nothing = []


class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    sound_manager = []
    reinforcement_manager = []
    request_port = 'center'  # 'center' or 'all' or 'none'
    frame_drop_corner = 'off'
    texture_caches = []
    phases = []

    ver = Ver('0.0.1')

    allowRepeats = True

    def __init__(tm, **kwargs):
        super(StandardVisionBehaviorTrialManager, tm).__init__(**kwargs)
        tm.sound_manager = kwargs['sound_manager']
        tm.reinforcement_manager = kwargs['reinforcement_manager']
        if 'request_port'in kwargs:
            tm.request_port = kwargs['request_port']
        if 'frame_drop_corner' in kwargs:
            tm.frame_drop_corner = kwargs['frame_drop_corner']

    def doTrial(tm, tR, station, **kwargs):
        # tm - trialManager
        # st - station
        # p - protocol
        # sub - subject
        # tR - trialRecord (current)
        # cR - compiledRecord
        # tR = kwargs['trialRecords']  # need to send this to _setup_phases
        tm._setup_phases(tR, station)  # should call calc_stim
        tm._validate_phases()
        tm._station_ok_for_trial_manager(station)

        # important data common to all trials
        tR = kwargs['trialRecords']
        tR.reinforcement_manager_name = tm.reinforcement_manager.name
        tR.reinforcement_manager_class = tm.reinforcement_manager.__class__.__name__

    def decache(tm):
        tm.TextureCaches = []
        return tm

    def _setup_phases(tm):
        raise NotImplementedError('Cannot run on an abstract class - call on a',
            ' concrete example')

    def compile_records(tm):
        pass


