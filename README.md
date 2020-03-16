# BCore

BCore is a Behavior training library built originally for training rodents but is compatible with training any subject. It was built in MATLab originally but is now compatible with python.

### See [Getting Started guide](https://github.com/balajisriram/BCore/blob/master/Docs/0.GettingStartedWithBCore.md) for details on installing and using BCore

## TODO:vant for 
 - [ ] Plot compiled_record. Filter last 10000 trials.
 - [ ] RunForReward trials
 - [ ] Flip trial\_pin on trial\_start in do\_trials
 - [ ] ZMQ output
 - [ ] Is session manager in protocol? Or in subject? Which spot makes the most sense?
 - [ ] Force IP address for a given computer
 - [ ] decide on license and execute
 - [ ] make module pip installable
 - [ ] configuration script
     - [ ] specify path to the data store location. verify write access
     - [ ] identify as standalone, client or server
 - [ ] add $BCOREPATH to path
 - [ ] configuration setup for bserver and bclient
	 - [ ] specify base path. [See here](https://github.com/balajisriram/bcore/blob/master/bcore/docs/1.DataModelForBCore.md#2)
	 - [ ] create .bcore in the basepath to contain relevant cofguration details for the installation
	 - [ ] create bcore data paths as required [See here](https://github.com/balajisriram/bcore/blob/master/bcore/docs/1.DataModelForBCore.md#2)
 - [ ] How are heats implemented?
 - [ ] Trial data - how to operationalize saving previous data and current data: pandas adding records is super slow