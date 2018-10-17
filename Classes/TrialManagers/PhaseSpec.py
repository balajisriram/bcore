__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

do_nothing = ()
class PhaseSpec(object):
    """
        PHASESPEC acts as a kind of state machine. You start at the first phase
        which specifies rules for moving through phases and keep going.
        stimulus: a stimulus object that is drawn on every frame
        stimulus_details: dictionary containing information specific to trial
        transitions: a dictionary
            {'port1':   target1,
             'port2',   target2,
             'port3',   target3,
             'timeout', target4}  timeout after framesUntilTransition
        frames_until_transition: used when 'timeout' is specified. Forced to
            float('inf') if no timeout is specified in transitions
        auto_trigger: a dictionary
            {'port1':   p1,
             'port2',   p2,
             'port3',   p3}
        phase_type: one of {'reinforced', None} --
            reinforced will ask the reinforcement manager how much water/airpuff
            to deliver at the beginning of the phase. A reward that extends
            beyond the end of the phase is cut off.
        phase_name: a text label for the given phase (stored in phaseRecords)
        sounds_played: (sound_name,sound_durnation_in_ms)
    """

    def __init__(self,
                 phase_number = 0,
                 stimulus = 0.5,
                 stimulus_details=None,
                 stimulus_update_fn=None,
                 transitions = {do_nothing: 1},
                 frames_until_transition = float('inf'),
                 auto_trigger = False,
                 phase_type = '',
                 phase_name = '',
                 pins_to_trigger = [],
                 hz = None,
                 sounds_played = {},
                 **kwargs):
        self.phase_number = phase_number
        self.stimulus = stimulus
        self.stimulus_details = stimulus_details
        self.stimulus_update_fn = stimulus_update_fn
        self.transitions = transitions
        self.frames_until_transition = frames_until_transition
        self.auto_trigger = auto_trigger
        self.hz = hz
        self.phase_type = phase_type
        self.phase_name = phase_name
        self.pins_to_trigger = pins_to_trigger
        self.sounds_played = sounds_played

    def __repr__(self):
        return "PhaseSpec object"

    def on_enter(self,trial_record, **kwargs):
        return trial_record

    def on_exit(self,trial_record, **kwargs):
        return trial_record


class StimPhaseSpec(PhaseSpec):
    """
        STIMPHASESPEC: use this simply to activate stim pin on_enter and switch
        it off on_exit
    """
    def __init__(self,
                 phase_number = 0,
                 stimulus = 0.5,
                 stimulus_details=None,
                 stimulus_update_fn=None,
                 transitions = {do_nothing: 1},
                 frames_until_transition = float('inf'),
                 auto_trigger = False,
                 phase_type = '',
                 phase_name = '',
                 pins_to_trigger = [],
                 hz = None,
                 sounds_played = {},
                 **kwargs):
        super(StimPhaseSpec,self).__init__(phase_number = phase_number,
                                             stimulus = stimulus,
                                             stimulus_details=stimulus_details,
                                             stimulus_update_fn=stimulus_update_fn,
                                             transitions = transitions,
                                             frames_until_transition = frames_until_transition,
                                             auto_trigger = auto_trigger,
                                             phase_type = phase_type,
                                             phase_name = phase_name,
                                             pins_to_trigger = pins_to_trigger,
                                             hz = hz,
                                             sounds_played = sounds_played,
                                             **kwargs)

    def __repr__(self):
        return "StimPhaseSpec object"

    def on_enter(self,station,trial_record,**kwargs):
        station.set_index_pin_on()
        trial_record['stim_on_time'] = station._clocks['trial_clock'].getTime()
        return trial_record

    def on_exit(self,station,trial_record,**kwargs):
        station.set_index_pin_off()
        trial_record['stim_off_time'] = station._clocks['trial_clock'].getTime()
        return trial_record


class RewardPhaseSpec(PhaseSpec):
    def __init__(self,
                 phase_number = 0,
                 stimulus = 0.5,
                 stimulus_details=None,
                 stimulus_update_fn=None,
                 transitions = {do_nothing: 1},
                 frames_until_transition = float('inf'),
                 auto_trigger = False,
                 phase_type = '',
                 phase_name = '',
                 pins_to_trigger = [],
                 hz = None,
                 sounds_played = {},
                 reward_valve = 'center_valve',
                 **kwargs):
        super(RewardPhaseSpec,self).__init__(phase_number = phase_number,
                                             stimulus = stimulus,
                                             stimulus_details=stimulus_details,
                                             stimulus_update_fn=stimulus_update_fn,
                                             transitions = transitions,
                                             frames_until_transition = frames_until_transition,
                                             auto_trigger = auto_trigger,
                                             phase_type = phase_type,
                                             phase_name = phase_name,
                                             pins_to_trigger = pins_to_trigger,
                                             hz = hz,
                                             sounds_played = sounds_played,
                                             **kwargs)
        self.reward_valve = reward_valve
        assert reward_valve in ['center_valve','left_valve','right_valve'], 'reward valve provided is unknown'

    def __repr__(self):
        return "RewardPhaseSpec object"

    def on_enter(self,station,trial_record,**kwargs):
        trial_record['correct'] = True
        trial_record['reward_duration'] = station._clocks['trial_clock'].getTime()
        return trial_record

    def on_exit(self,station,trial_record,**kwargs):
        station.close_valve(self.reward_valve)
        trial_record['reward_duration'] = station._clocks['trial_clock'].getTime() - trial_record['reward_duration']
        return trial_record

class PunishmentPhaseSpec(PhaseSpec):
    def __init__(self,
                 phase_number = 0,
                 stimulus = 0.5,
                 stimulus_details=None,
                 stimulus_update_fn=None,
                 transitions = {do_nothing: 1},
                 frames_until_transition = float('inf'),
                 auto_trigger = False,
                 phase_type = '',
                 phase_name = '',
                 pins_to_trigger = [],
                 hz = None,
                 sounds_played = {},
                 **kwargs):
        super(PunishmentPhaseSpec,self).__init__(phase_number = phase_number,
                                                 stimulus = stimulus,
                                                 stimulus_details=stimulus_details,
                                                 stimulus_update_fn=stimulus_update_fn,
                                                 transitions = transitions,
                                                 frames_until_transition = frames_until_transition,
                                                 auto_trigger = auto_trigger,
                                                 phase_type = phase_type,
                                                 phase_name = phase_name,
                                                 pins_to_trigger = pins_to_trigger,
                                                 hz = hz,
                                                 sounds_played = sounds_played,
                                                 **kwargs)

    def __repr__(self):
        return "PunishmentPhaseSpec object"

    def on_enter(self,trial_record,**kwargs):
        trial_record['correct'] = False
        return trial_record

    def on_exit(self, trial_record,**kwargs):
        return trial_record
