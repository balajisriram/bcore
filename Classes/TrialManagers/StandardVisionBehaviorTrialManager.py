from .TrialManager import TrialManager
from verlib import NormalizedVersion as Ver

do_nothing = []


class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    phases = []

    ver = Ver('0.0.1')

    allow_repeats = True

    def __init__(tm, 
	             name = 'DefaultVisBehTrManager',
                 sound_manager = None, 
				 reinforcement_manager = None, 
				 text_display='full', 
				 **kwargs):
        super(StandardVisionBehaviorTrialManager, tm).__init__(name, **kwargs)
        tm.sound_manager = sound_manager
        tm.reinforcement_manager = reinforcement_manager
        tm.text_display = text_display

        assert tm.text_display in ['full', 'light', 'off'], "text_display not one of ['full','light','off']"

    def do_trial(tm, tR, station, **kwargs):
        # tm - trialManager
        # st - station
        # p - protocol
        # sub - subject
        # tR - trialRecord (current)
        # cR - compiledRecord
        # tR = kwargs['trialRecords']  # need to send this to _setup_phases
        tm._setup_phases(tR, station, **kwargs)  # should call calc_stim
        tm._validate_phases()
        tm._station_ok_for_trial_manager(station)

        # important data common to all trials
        tR = kwargs['trialRecords']
        tR.reinforcement_manager_name = tm.reinforcement_manager.name
        tR.reinforcement_manager_class = tm.reinforcement_manager.__class__.__name__

    def decache(tm):
        return tm

    def _setup_phases(tm):
        raise NotImplementedError('Cannot run on an abstract class - call on a',
            ' concrete example')

    def compile_records(tm):
        pass


