# BCore

## Introduction
BCore is a Behavior training library built originally for training rodents but is compatible with training any subject. It was built in MATLab originally but is now compatible with python.

## Starting with BCore
 * use anaconda with BCore
 * For an example, run python -m BCore.Bootstrap.StandAloneRun

## Installation:
1. _git clone www.github.com/balajisriram/BCore.git_. Note this will also create a Folder in the same location for all the data collected during running experiments
2. Install miniconda in Windows or Linux
3. _conda create -n psychopy --file environment.yml_ and _source activate psychopy_
4. _pip install -r piplist.txt_
5. _python -m BCore.Bootstrap.StandAloneRun_. See StandAloneRun for details on how to call the function.

## TODO:
 - [ ] Plot compiled_record. Filter last 10000 trials.
 - [ ] RunForReward trials
 - [ ] Flip trial_pin on trial_start in do_trials
 - [ ] ZMQ output
