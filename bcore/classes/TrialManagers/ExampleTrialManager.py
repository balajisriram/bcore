class ExampleTrialManager(object):
    """
        EXAMPLETRIALMANAGER defines a standard trial manager
            input_feature_1
            input_feature_2
    """
    _Phases = []
    _trial_specific_details_1 = []
    _trial_specific_details_1 = []

    def __init__(self,
                 name = 'DemoExampleTrialManager',
                 input_feature_1 = 'default1',
                 input_feature_2 = 'default2',
                 **kwargs):
        self.ver = Ver('0.0.1')
        self.name = name
        self.reinforcement_manager = reinforcement_manager

        self.input_feature_1 = input_feature_1
        self.input_feature_2 = input_feature_2
        
        # do QC on the inputs
        self.verify_params_ok()
    
    def verify_params_ok(self):
        assert self.input_feature_1=='default1','EXAMPLETRIALMANAGER::INIT::input_feature_1 is incorrect'
        assert self.input_feature_2=='default2','EXAMPLETRIALMANAGER::INIT::input_feature_2 is incorrect'
        
    @property
    def n_afc():
        return len(self.deg_per_cycs)

    @staticmethod
    def update_stimulus(stimulus,details):
        if details['drift_frequency'] !=0:
            stimulus.phase += float(details['drift_frequency'])/float(details['Hz'])

    @staticmethod
    def do_nothing_to_stim(stimulus,details):
        pass
        
    def __repr__(self):
        return "ExampleTrialManager object"

    def choose_ports(self, trial_record, station, ):
        pass

    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record
        # resetup the window according to the itl

        # check if okay to run the trial manager with the station
        if not self.station_ok_for_tm(station):
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit


        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record, subject=subject)
        station._key_pressed = []

        current_phase_num = 0

        # was on will be used to check for new responses
        was_on = {'L':False, 'C': False, 'R':False}

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
            if phase.sounds_played:
                sound = phase.sounds_played[0]
                sound_duration = phase.sounds_played[1]
                sound.seek(0.)
                sound_started = False
                sound_done = False
                sound_timer = psychopy.core.CountdownTimer(sound_duration)
            else:
                sound = None

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
                if sound:
                    if not sound_started:
                        sound.play()
                        sound_timer.reset()
                        sound_started = True

                    if sound_timer.getTime() <0 and not sound_done:
                        sound.stop()
                        sound_done = True

                # deal with stim
                if stim:
                    stim.draw()
                    if phase.phase_name=='stim':
                        psychopy.visual.Rect(station._window,pos=(-300,-300),width=100,height=100,units='pix',fillColor=(1,1,1)).draw()
                    phase.stimulus_update_fn(stim,stim_details)
                phase.on_frame(station=station,trial_record=trial_record)

                # look for responses
                response_led_to_transition = False
                response = station.read_ports()
                if len(response)>1:
                    error_out = True
                    trial_record['errored_out'] = True
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
                # phase is done when there are no more frames in the phase or is we flipped due to transition
                # however we can stop playing the phase because we manual_quit or because we errored out
                frames_until_transition = frames_until_transition-1
                frames_led_to_transition = False
                if frames_until_transition==0:
                    frames_led_to_transition = True
                    if transition: current_phase_num = transition[None] - 1
                    else: current_phase_num = None # the last phase has no

                if frames_led_to_transition or response_led_to_transition:
                    phase_done = True
                manual_quit = station.check_manual_quit()
                if manual_quit:
                    trial_record['manual_quit'] = True
                    trial_record['correct'] = None
                quit = quit or manual_quit
            trial_record = phase.on_exit(trial_record=trial_record, station=station)
            trial_record['phase_data'].append(phase_data)

            # when do we quit the trial? trial_done only when last phjase
            # but we can exit if manual_quit or errored out
            if is_last_phase: trial_done = True
        station.set_trial_pin_off()
        return trial_record,quit

    def calc_stim(self, trial_record, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        all_ports = ('L','C','R')
        request_port = 'C'
        response_ports = tuple(np.setdiff1d(all_ports,request_port))
        target_port = np.random.choice(response_ports)
        distractor_port = tuple(np.setdiff1d(response_ports,target_port))

        distractor_port = distractor_port[0]
        # select from values
        stimulus = dict()
        stimulus['deg_per_cyc'] = random.choice(self.deg_per_cycs[target_port])
        stimulus['orientation'] = random.choice(self.orientations[target_port])
        stimulus['drift_frequency'] = random.choice(self.drift_frequencies[target_port])
        stimulus['phase'] = random.choice(self.phases[target_port])
        stimulus['contrast'] = random.choice(self.contrasts[target_port])
        stimulus['duration'] = random.choice(self.durations[target_port])
        stimulus['location'] = random.choice(self.locations[target_port])
        stimulus['radius'] = random.choice(self.radii[target_port])
        stimulus['radius_type'] = self.radius_type
        stimulus['H'] = H
        stimulus['W'] = W
        stimulus['Hz'] = Hz

        trial_record['chosen_stim'] = stimulus

        frames_total = round(Hz*stimulus['duration'])

        port_details = {}
        port_details['request_port'] = request_port
        port_details['target_port'] = target_port
        port_details['distractor_port'] = distractor_port

        return stimulus, resolution, frames_total, port_details

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def _setup_phases(self, trial_record, station, subject, **kwargs):
        """
        AFCGratings:_setup_phases
        1. Pre-trial: gray screen. REQUEST_PORT -> 2
        2. Stimulus: Grating stimulus. RESPONSE_PORT==TARGET_PORT -> CORRECT, else PUNISH
        3. Correct: Give reward
        4. Punish: Timeout
        5. ITI: Gray screen of duration iti,
        """
        (stimulus_details,resolution,frames_total,port_details) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        if port_details['target_port'] == 'L':
            reward_valve = 'left_valve'
        elif port_details['target_port'] == 'R':
            reward_valve = 'right_valve'
        elif port_details['target_port'] == 'C':
            reward_valve = 'center_valve'

        if stimulus_details['duration']==float('inf'):
            do_post_discrim_stim = False
        else:
            do_post_discrim_stim = True

        self._Phases = []

        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = self.reinforcement_manager.calculate_reinforcement(subject=subject)
        reward_size = np.round(reward_size/1000*60)
        request_reward_size = np.round(request_reward_size/1000*60)
        penalty_size = np.round(ms_penalty/1000*60)
        if do_post_discrim_stim:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['request_port']: 2},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='pre-request',
                phase_name='pre-request',
                hz=hz,
                sounds_played=(station._sounds['trial_start_sound'], 0.050)))
            if self.radius_type=='Gaussian':
                self._Phases.append(PhaseSpec(
                    phase_number=2,
                    stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='gauss',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                    stimulus_update_fn=AFCGratings.update_stimulus,
                    stimulus_details=stimulus_details,
                    transitions={None: 3, port_details['target_port']: 4, port_details['distractor_port']: 5},
                    frames_until_transition=frames_total,
                    auto_trigger=False,
                    phase_type='stimulus',
                    phase_name='stim',
                    hz=hz,
                    sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            else:
                self._Phases.append(PhaseSpec(
                    phase_number=2,
                    stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='circle',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                    stimulus_update_fn=AFCGratings.update_stimulus,
                    stimulus_details=stimulus_details,
                    transitions={None: 3, port_details['target_port']: 4, port_details['distractor_port']: 5},
                    frames_until_transition=frames_total,
                    auto_trigger=False,
                    phase_type='stimulus',
                    phase_name='stim',
                    hz=hz,
                    sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            self._Phases.append(PhaseSpec(
                phase_number=3,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['target_port']: 4, port_details['distractor_port']: 5},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='post-stimulus',
                phase_name='post-stim',
                hz=hz,
                sounds_played=None))
            self._Phases.append(RewardPhaseSpec(
                phase_number=4,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 6},
                frames_until_transition=reward_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='reward',
                hz=hz,
                sounds_played=(station._sounds['correct_sound'], ms_reward_sound/1000),
                reward_valve=reward_valve))
            self._Phases.append(PunishmentPhaseSpec(
                phase_number=5,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(0.,0.,0.,),autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 6},
                frames_until_transition=penalty_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='punishment',
                hz=hz,
                sounds_played=(station._sounds['punishment_sound'],ms_penalty_sound/1000)))
            self._Phases.append(PhaseSpec(
                phase_number=6,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_details=None,
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                transitions=None,
                frames_until_transition=round(self.iti*hz),
                auto_trigger=False,
                phase_type='inter-trial',
                phase_name='inter-trial',
                hz=hz,
                sounds_played=(station._sounds['trial_end_sound'], 0.050)))
        else:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['request_port']: 2},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='pre-request',
                phase_name='pre-request',
                hz=hz,
                sounds_played=(station._sounds['trial_start_sound'], 0.050)))
            if self.radius_type=='Gaussian':
                self._Phases.append(PhaseSpec(
                    phase_number=2,
                    stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='gauss',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                    stimulus_update_fn=AFCGratings.update_stimulus,
                    stimulus_details=stimulus_details,
                    transitions={port_details['target_port']: 3, port_details['distractor_port']: 4},
                    frames_until_transition=float('inf'),
                    auto_trigger=False,
                    phase_type='stimulus',
                    phase_name='stim',
                    hz=hz,
                    sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            else:
                self._Phases.append(PhaseSpec(
                    phase_number=2,
                    stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='circle',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                    stimulus_update_fn=AFCGratings.update_stimulus,
                    stimulus_details=stimulus_details,
                    transitions={port_details['target_port']: 3, port_details['distractor_port']: 4},
                    frames_until_transition=float('inf'),
                    auto_trigger=False,
                    phase_type='stimulus',
                    phase_name='stim',
                    hz=hz,
                    sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            self._Phases.append(RewardPhaseSpec(
                phase_number=3,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 5},
                frames_until_transition=reward_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='reward',
                hz=hz,
                sounds_played=(station._sounds['correct_sound'], ms_reward_sound/1000),
                reward_valve=reward_valve))
            self._Phases.append(PunishmentPhaseSpec(
                phase_number=4,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(0,0,0,),autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 5},
                frames_until_transition=penalty_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='punishment',
                hz=hz,
                sounds_played=(station._sounds['punishment_sound'],ms_penalty_sound/1000)))
            self._Phases.append(PhaseSpec(
                phase_number=5,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_details=None,
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                transitions=None,
                frames_until_transition=round(self.iti*hz),
                auto_trigger=False,
                phase_type='inter-trial',
                phase_name='inter-trial',
                hz=hz,
                sounds_played=(station._sounds['trial_end_sound'], 0.050)))

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardVisionBehaviorStation','StandardKeyboardStation']:
            return True
        else:
            return False

    def trial_compiler(self, compiled_record, trial_record):
        try:
            compiled_details = compiled_record['compiled_details']['AFCGratings']
        except KeyError:
            compiled_details = {}
            compiled_details['trial_number'] = []
            compiled_details['deg_per_cyc'] = []
            compiled_details['orientation'] = []
            compiled_details['drift_frequency'] = []
            compiled_details['phase'] = []
            compiled_details['contrast'] = []
            compiled_details['duration'] = []
            compiled_details['location'] = []
            compiled_details['radius'] = []
            compiled_details['radius_type'] = []
            compiled_details['H'] = []
            compiled_details['W'] = []
            compiled_details['Hz'] = []
            # specific to animal responses
            compiled_details['request_time'] = [] # time from trial start to center request
            compiled_details['response_time'] = [] # time from request to response
            compiled_details['request_lick_timings'] = []
            compiled_details['response_lick_timings_prev_trial'] = []
            # put an empty compiled_details in the compiled_records
            compiled_record['compiled_details']['Gratings'] = compiled_details

        compiled_details['trial_number'].append(trial_record['trial_number'])
        compiled_details['deg_per_cyc'].append(trial_record['chosen_stim']['deg_per_cyc'])
        compiled_details['orientation'].append(trial_record['chosen_stim']['orientation'])
        compiled_details['drift_frequency'].append(trial_record['chosen_stim']['drift_frequency'])
        compiled_details['phase'].append(trial_record['chosen_stim']['phase'])
        compiled_details['contrast'].append(trial_record['chosen_stim']['contrast'])
        compiled_details['duration'].append(trial_record['chosen_stim']['duration'])
        compiled_details['location'].append(trial_record['chosen_stim']['location'])
        compiled_details['radius'].append(trial_record['chosen_stim']['radius'])
        compiled_details['radius_type'].append(self.radius_type)
        compiled_details['H'].append(trial_record['chosen_stim']['H'])
        compiled_details['W'].append(trial_record['chosen_stim']['W'])
        compiled_details['Hz'].append(trial_record['chosen_stim']['Hz'])

        # animal response data compilation
        phase_data = trial_record['phase_data']
        phase_types = np.asarray([p['phase_type'] for p in phase_data])
        pre_req_phase_num = np.argwhere(phase_types=='pre-request')
        stim_phase_num = np.argwhere(phase_types=='stimulus')
        reinf_phase_num = np.argwhere(phase_types=='reinforcement')
        # request_time is time from TRIAL_START to 'stim' phase enter_time
        compiled_details['request_time'].append(phase_data[stim_phase_num]['enter_time'])
        # resonse_time is time from 'stim' phase enter_time to 'reinforcement' phase enter time
        compiled_details['response_time'].append(phase_data[reinf_phase_num]['enter_time']-phase_data[stim_phase_num]['enter_time'])
        # request_lick_timings are 'C' licks in the stim_phase
        lick_loc = np.asarray(phase_data[stim_phase_num]['response'])
        lick_times = np.asarray(phase_data[stim_phase_num]['response_time'])
        which_licks = np.argwhere(lick_loc=='C')
        compiled_details['request_lick_timings'].append(lick_times[which_licks])
        # response_lick_timings_prev_trial are non 'C' licks in the pre_req_phase_num
        lick_loc = np.asarray(phase_data[pre_req_phase_num]['response'])
        lick_times = np.asarray(phase_data[pre_req_phase_num]['response_time'])
        which_licks = np.argwhere(lick_loc!='C')
        compiled_details['response_lick_timings_prev_trial'].append(lick_times[which_licks])




        compiled_record['compiled_details'] = compiled_details

        return compiled_details

