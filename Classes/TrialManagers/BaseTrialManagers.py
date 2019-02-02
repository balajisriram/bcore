from verlib import NormalizedVersion as Ver
import numpy as np
import psychopy.visual
from psychopy.constants import (STARTED, PLAYING, PAUSED, FINISHED, STOPPED,
                                NOT_STARTED, FOREVER)

################################# BASETRIALMANAGER ##################################
class BaseTrialManager(object):
    """
        BASETRIALMANAGER defines a trial manager that defines a do_trial() method

        VERSION HISTORY:
        0.0.1: Setup BaseTrial Manager as superclass of all trial managers
        0.0.2: BTM defines (1) inter-trial-interval, (2) inter-trial-luminance
               (3) defines was_on based on the characteristics of station
               (4) try_something_else sound turns on when triggering port without a
               trasition target
               (5)

    """
    _Phases = []
    def __init__(self,draw_stim_onset_rect = False, iti=1.0, itl=(0., 0., 0.)):
        self.ver = Ver('0.0.2')
        self.draw_stim_onset_rect = draw_stim_onset_rect
        self.iti = iti
        if np.isscalar(itl):
            self.itl = itl*np.asarray([1,1,1]) # inter trial luminance as gray scale
        else:
            self.itl = np.asarray(itl) #itl as color

    def __repr__(self):
        return "BaseTrialManager trial manager object"

    @staticmethod
    def do_nothing_to_stim(stimulus,details):
        pass

    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record. Called by other trial managers

        from psychopy import logging
        logging.console.setLevel(logging.ERROR)

        do_nothing = ()

        current_phase_num = 0

        # was on will be used to check for new responses
        all_ports = station.get_ports()
        was_on = {}
        for port in all_ports:
            was_on[port] = False

        # Zero out the trial clock
        trial_clock = station._clocks['trial_clock']
        trial_clock.reset()

        trial_done = False
        error_out = False

        trial_record['errored_out'] = False
        trial_record['manual_quit'] = False


        trial_record['reinforcement_manager_name'] = self.reinforcement_manager.name
        trial_record['reinforcement_manager_class'] = self.reinforcement_manager.__class__.__name__
        trial_record['reinforcement_manager_version_number'] = self.reinforcement_manager.ver.__str__()

        trial_record['phase_data'] = []

        # What to do if response cannot lead to any thing??
        try_something_else_sound = station._sounds['try_something_else']
        try_something_else_sound_status = NOT_STARTED
        try_something_else_sound_played_for = None
        # first response after transition should not trigger a try_something_else_sound until that response ended
        response_that_led_to_transition = None # response that led to transition for previous phase
        transitioned_response_ended = True # did that previous transition end?


        station.set_trial_pin_on()
		
		# text stim to denote trial
		trial_number_text = psychopy.visual.TextStim(station._window,
		    text='trial_number::{0}'.format(trial_record['trial_number']), 
		    pos=(-0.95,-0.95), units='norm', height=0.02, )
		
        ### loop into trial phases
        while not trial_done and not error_out and not quit:
            # current_phase_num determines the phase
            phase = self._Phases[current_phase_num]

            # collect details about the phase
            frames_until_transition = phase.frames_until_transition
            stim = phase.stimulus
            stim_details = phase.stimulus_details
            transition = phase.transitions
            if not transition:
                is_last_phase = True
            else:
                is_last_phase = False
            auto_trigger = phase.auto_trigger

            # save relevant data into phase_data
            phase_data = {}
            phase_data['phase_name'] = phase.phase_name
            phase_data['phase_number'] = phase.phase_number
            phase_data['enter_time'] = trial_clock.getTime()
            phase_data['response'] = []
            phase_data['response_time'] = []

            # loop into phase
            phase_done = False
            trial_record = phase.on_enter(trial_record=trial_record, station=station)
            while not phase_done and not error_out and not quit:
                # deal with sounds
                if phase.sounds_played:
                    for snd in phase.sounds_played:
                        if snd.status==NOT_STARTED: snd.play()
                # deal with stim
                if stim:
                    stim.draw()
                    if self.draw_stim_onset_rect and phase.phase_type=='stim':
                        psychopy.visual.Rect(station._window,pos=(-300,-300),width=100,height=100,units='pix',fillColor=(1,1,1)).draw()
                    phase.stimulus_update_fn(stim,stim_details)
				trial_number_text.draw()
				
                phase.on_frame(station=station,trial_record=trial_record)

                # look for responses
                # (1) if no responses, only thing to do is stop the try_something_else_sound if its playing. then, switch off
                #     any was_on previously set to True
                # (2) if response length >1 -> ERROR
                # (3) if response is unique, log it as long as the response wasn't on before
                #     (a) if it leads to transition, set the current phase num appropriately
                #     (b) if there is no transition for response or if there is no transition , try_something_else_sound
                #        (except if the response is the ending of previous trigger)
                #
                response_led_to_transition = False
                response = station.read_ports()
                if len(response)>1:
                    error_out = True
                    trial_record['errored_out'] = True
                    print('BASETRIALMANAGER:DO_TRIAL:errored out due to multiple responses')
                elif len(response)==1:
                    response = response[0]
                    if transition and response in transition:
                        current_phase_num = transition[response]
                        response_led_to_transition = True
                        response_that_led_to_transition = response
                        transitioned_response_ended = False # will flip to True the first time response_that_led_to_transition is no longer available
                    else:
                        # there was a response and it didnt lead to transition -> try something else
                        if (response is not response_that_led_to_transition or transitioned_response_ended) and try_something_else_sound_status == NOT_STARTED:
                            try_something_else_sound.play()
                            try_something_else_sound_status = STARTED
                            try_something_else_sound_played_for = response

                    # logit but only if was_on wasnt already on. thus only response onsets are measured.
                    if not was_on[response]:
                        phase_data['response'].append(response)
                        phase_data['response_time'].append(trial_clock.getTime())
                    was_on[response] = True # flip was on to true after we used it to check for new events
                else:
                    # try somethign else has to go through a no_response phase otherwise, it will error out!!
                    if try_something_else_sound_status==STARTED:
                        try_something_else_sound.stop()
                        try_something_else_sound_status = NOT_STARTED
                        try_something_else_sound_played_for = None
                    for resp in was_on:was_on[resp] = False
                    transitioned_response_ended=True # force to True. Wont come here unless the transitioned response ended

                # update the frames_until_transition and check if the phase is done
                # phase is done when there are no more frames in the phase or if we flipped due to transition
                # however we can stop playing the phase because we manual_quit or because we errored out
                frames_until_transition = frames_until_transition-1
                frames_led_to_transition = False
                autotrigger_led_to_transition = False
                if frames_until_transition==0 and transition and do_nothing in transition:
                    frames_led_to_transition = True
                    current_phase_num = transition[do_nothing]
                elif frames_until_transition==0 and transition is None:
                    current_phase_num = None
                    phase_done = True
                    trial_done = True
                    print('BASETRIALMANAGER:DO_TRIAL:end of trial')
                else:
                    RuntimeError("transition cannot have frames go to zero without a do_nothing possibility")
                if frames_led_to_transition or response_led_to_transition:
                    phase_done = True
                manual_quit = station.check_manual_quit()
                if manual_quit:
                    print('BASETRIALMANAGER:DO_TRIAL:manual quit')
                    trial_record['manual_quit'] = True
                    trial_record['correct'] = None
                quit = quit or manual_quit

                if (phase_done or quit) and phase.sounds_played:
                    for snd in phase.sounds_played: snd.stop()

            trial_record = phase.on_exit(trial_record=trial_record, station=station)
            trial_record['phase_data'].append(phase_data)

            # when do we quit the trial? trial_done only when last phase
            # but we can exit if manual_quit or errored out
            if is_last_phase: trial_done = True
        station.set_trial_pin_off()
        return trial_record,quit
