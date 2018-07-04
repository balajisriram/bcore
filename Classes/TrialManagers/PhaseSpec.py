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

    def on_enter (self):
        pass

    def on_exit(self):
        pass