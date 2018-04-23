__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

do_nothing = []
class PhaseSpec(object):
    """
        PHASESPEC acts as a kind of state machine. You start at the first phase
        which specifies rules for moving through phases and keep going.
        stimType:
            allowed:'static', - explicitly call for flip
                    'cache', - relevant texs are stored in stimManager cache
                    'loop', - given stims are looped
                    {'timedFrames', numFrames}, - present 'numFrames' frames
                    'expert' - use trial_manager.draw_expert_frame()
            default is 'loop'
        stimulus: a dictionary containing
            scaleFactor, hz and frames for ('static', 'cache','loop')
                OR
            struct (for 'expert' phase)
        transitions: a dictionary
            {'port1':   target1,
             'port2',   target2,
             'port3',   target3,
             'timeout', target4}  timeout after framesUntilTransition
        framesUntilTransition: used when 'timeout' is specified. Forced to
            float('inf') if no timeout is specified in transitions
        autoTrigger: a dictionary
            {'port1':   p1,
             'port2',   p2,
             'port3',   p3}
        isFinalPhase: a flag if this is the final phase of the trial
        phaseType: one of {'reinforced', None} --
            reinforced will ask the reinforcement manager how much water/airpuff
            to deliver at the beginning of the phase. A reward that extends
            beyond the end of the phase is cut off.
        phaseName: a text label for the given phase (stored in phaseRecords)
        isStim: status of station's stim pin for phase(True/ False)
        indexPulses: a boolean vector same length as stimulus
            indicating what to output on the station's indexPin during each
            frame (defaults to all False)
    """
    frames_until_transition = float('inf')
    soundPlayed = {}

    def __init__(self,
                 phase_number = 0,
                 stimulus = 0.5,
                 stim_type = 'loop',
                 start_frame = 0,
                 transitions = {do_nothing: 1},
                 frames_until_transition = float('inf'),
                 auto_trigger = False,
                 is_final_phase = True,
                 phase_type = '',
                 phase_name = '',
                 pins_to_trigger = [],
                 sounds_played = {},
                 **kwargs):
        self.phase_number = phase_number
        self.stimulus = stimulus
        self.stim_type = stim_type
        self.start_frame = start_frame
        self.transitions = transitions
        self.frames_until_transition = frames_until_transition
        self.auto_trigger = auto_trigger
        self.is_final_phase = is_final_phase
        self.hz = kwargs['hz']
        self.phase_type = phase_type
        self.phase_name = phase_name
        self.pins_to_trigger = pins_to_trigger
        self.sounds_played = sounds_played

    def on_enter (self):
        pass

    def on_exit(self):
        pass