from verlib import NormalizedVersion as Ver

from psychopy.constants import (STARTED, PLAYING, PAUSED, FINISHED, STOPPED,
                                NOT_STARTED, FOREVER)

################################# BASETRIALMANAGER ##################################
class BaseTrialManager(object):
    """
        BASETRIALMANAGER defines a trial manager that defines a do_trial() method
    """
    def __init__(self,draw_stim_onset_rect = False):

        self.draw_stim_onset_rect = draw_stim_onset_rect

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
        was_on = {'response_port':False}

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

        station.set_trial_pin_on()
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
                phase.on_frame(station=station,trial_record=trial_record)

                # look for responses
                response_led_to_transition = False
                response = station.read_ports()
                if len(response)>1:
                    error_out = True
                    trial_record['errored_out'] = True
                    print('BASETRIALMANAGER:DO_TRIAL:errored out')
                elif len(response)==1:
                    response = response[0]
                    try:
                        current_phase_num = transition[response] - 1
                        response_led_to_transition = True
                    except KeyError:
                        response_led_to_transition = False # that phase did not have a transition for that response
                    except TypeError:
                        assert is_last_phase, 'No reason why it should come here otherwise'
                    finally:
                        # logit but only if was_on wasnt already on
                        if not was_on[response]:
                            phase_data['response'].append(response)
                            phase_data['response_time'].append(trial_clock.getTime())
                    was_on[response] = True # flip was on to true after we used it to check for new events
                else:
                    pass

                # update the frames_until_transition and check if the phase is done
                # phase is done when there are no more frames in the phase or if we flipped due to transition
                # however we can stop playing the phase because we manual_quit or because we errored out
                frames_until_transition = frames_until_transition-1
                frames_led_to_transition = False
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

            # when do we quit the trial? trial_done only when last phjase
            # but we can exit if manual_quit or errored out
            if is_last_phase: trial_done = True
        station.set_trial_pin_off()
        return trial_record,quit

