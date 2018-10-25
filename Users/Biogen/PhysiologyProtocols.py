__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

from BCore.Classes.Protocol import StartsAtOneProtocol, TrainingStep
from BCore.Classes.Criterion import RepeatIndefinitely, NumTrialsDoneCriterion
from BCore.Classes.SessionManager import NoTimeOff
from BCore.Classes.TrialManagers.GratingsTrialManagers import Gratings
from BCore.Classes.ReinforcementManager import NoReinforcement

def get_orientation_tuning_protocol():
    training_steps = [TrainingStep(
    name='or_tuning_ts_8_ors_drift_2Hz_2s_fullC',
    trial_manager=Gratings(name='phys_or_tuning_trial_manager',
                           deg_per_cycs=[0.1],
                           orientations=[0,45,90,135,180,225,270,315],
                           contrasts=[1.],
                           durations=[2.],
                           radii=[400],
                           drift_frequencies=[2.],
                           iti=1., itl=0.),
    session_manager=NoTimeOff(),
    criterion=RepeatIndefinitely(),
    )]
    return StartsAtOneProtocol(training_steps=training_steps, name='or_tuning_protocol_biogen_08292018')

def get_short_duration_protocol():
    ts1 = TrainingStep(name='or_tuning_ts_8_ors_drift_2Hz_2s_fullC',
                       trial_manager=Gratings(name='phys_or_tuning_trial_manager',
                                              deg_per_cycs=[0.1],
                                              orientations=[0,45,90,135,180,225,270,315],
                                              contrasts=[1.],
                                              durations=[2.],
                                              radii=[400],
                                              drift_frequencies=[2.],
                                              iti=1., itl=0.),
                        session_manager=NoTimeOff(),
                        criterion=NumTrialsDoneCriterion(num_trials=200,num_trials_mode='consecutive'))
    ts2 = TrainingStep(name='short_duration_pm45deg_8phases',
                       trial_manager=Gratings(name='phys_or_tuning_trial_manager',
                                              deg_per_cycs=[0.1],
                                              orientations=[45,-45],
                                              contrasts=[1.,0.15],
                                              durations=[0.05,0.1,0.15,0.2],
                                              radii=[400],
                                              iti=1., itl=0.),
                        session_manager=NoTimeOff(),
                        criterion=RepeatIndefinitely())
    training_steps = [ts1,ts2]
    return StartsAtOneProtocol(training_steps=training_steps, name='short_duration_protocol_biogen_08292018')

def get_phys_protocol_biogen(name='orientation_tuning_biogen_08292018'):
    if name=='orientation_tuning_biogen_08292018':
        return get_orientation_tuning_protocol()
    elif name=='short_duration_biogen_08292018':
        return get_short_duration_protocol()
