"""
    1. Drop into BASECONFIGFORM
"""
import npyscreen as nps
import json
import os

from bcore import get_ip_addr

################################################################################
##############################       UTILITY      ##############################
################################################################################

def get_base_path():
    # returns the directory under the BCore directory
    base = os.path.split(os.path.abspath(__file__))
    base = os.path.split(base[0])
    base = os.path.split(base[0])
    base = os.path.split(base[0])
    return base[0]

def get_database_path():
    return os.path.join(get_base_path(),'BCoreData')

def get_config_path():
    return os.path.join(get_base_path(),'.bcore')

################################################################################
###############################       FORMS      ###############################
################################################################################

class BaseConfigForm(nps.ActionForm):
    def create(self):
        self.nextrely=5
        self.base_path = self.add(nps.TitleFilenameCombo, name="Provide data base path:",value=get_database_path(),select_dir=True,must_exist=True,confirm_if_exists=True)
        self.bcore_mode = self.add(nps.TitleSelectOne, max_height=5, value = [1,], name="How will this BCore installation work? Pick One:",values = ["Server","Client","Stand Alone"], scroll_exit=True)
        self.ip_addr = self.add(nps.TitleText, name="Your IP address (you can change this is the detailsed config form):",value = get_ip_addr(), scroll_exit=False,editable=False)
        self.detail_config = self.add(nps.CheckBox,name="Further configure install?")
        
    def on_ok(self):
        configuration = dict()
        configuration['base_path'] = self.base_path.value
        configuration['mode'] = self.bcore_mode.values[self.bcore_mode.value[0]]
        configuration['ip_addr'] = self.ip_addr.value
        
        configuration_text = "base_path::{0}\nmode::{1}\n".format(self.base_path.value,self.bcore_mode.values[self.bcore_mode.value[0]])
        if self.detail_config.value:
            configuration_text = configuration_text+'Will move to next form as we further configure the installation\n'
            if configuration['mode']=='Server':
                try:
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','ServerData','backup'))
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','SubjectData','History'))
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','TrialData'))
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','StationData'))
                except FileExistsError: pass
                    
                self.parentApp.setNextForm('SERVER_CONFIG')
            elif configuration['mode']=='Client':
                try:
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','SubjectData'))
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','StationData'))
                except FileExistsError: pass
                    
                self.parentApp.setNextForm('CLIENT_CONFIG')
            else:
                try:
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','ServerData','backup'))
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','SubjectData','History'))
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','TrialData'))
                    os.makedirs(os.path.join(configuration['base_path'],'BCoreData','StationData'))
                except FileExistsError: pass
                    
                self.parentApp.setNextForm('STANDALONE_CONFIG')
        else:
            self.parentApp.setNextForm(None)
            
        nps.notify_confirm('Saving configuration at {0}\n\n{1}'.format(get_config_path(),configuration_text),'OK Button',editw=1,wide=True)
        self.parentApp.basic_config = configuration
        
        # now create the directory and save the data
        try:
            os.makedirs(get_config_path())
        except FileExistsError:
            pass
        with open(os.path.join(get_config_path(),'bcore.config'),'w') as f:
            json.dump(configuration,f,indent=4)

    def on_cancel(self):
        nps.notify_confirm("No changes have been made to configuration. Re-run install/configure.py to configure your installation",'Exiting',editw=1)
        self.parentApp.setNextForm(None)
        
class ConfigureServer(nps.ActionFormWithMenus):
    def create(self):
        self.server_name = self.add(nps.TitleText, name="Name your server",value = "server-001", scroll_exit=False,editable=True)

        self.ip_addr = self.add(nps.TitleText, name="Your IP address:",value = get_ip_addr(), scroll_exit=False,editable=True)
        self.subnet_mask = self.add(nps.TitleText, name="Your subnet mask address:",value = '255.255.255.0', scroll_exit=False,editable=True)
        self.gateway = self.add(nps.TitleText, name="Your gateway address:",value = '192.168.0.1', scroll_exit=False,editable=True)
        self.port = self.add(nps.TitleText, name="Your port number:",value = '5550', scroll_exit=False,editable=True)
        
        self.ADD_SUBJECT = self.add(AddSubjectButtonPress,name="Add a subject")
        self.ADD_STATION = self.add(AddStationButtonPress,name="Add a station")
                
        
    def on_ok(self):
        self.parentApp.setNextForm(None)
        
    def on_cancel(self):
        nps.notify_confirm("No changes have been made to configuration",'Exiting',editw=1)
        self.parentApp.setNextForm(None)


class ConfigureClient(nps.ActionForm):
    def create(self):
        pass
        
    def on_ok(self):
        self.parentApp.setNextForm(None)
        
    def on_cancel(self):
        nps.notify_confirm("No changes have been made to configuration",'Exiting',editw=1)
        self.parentApp.setNextForm(None)


class ConfigureStandAlone(nps.ActionForm):
    def create(self):
        pass
        
    def on_ok(self):
        self.parentApp.setNextForm(None)
        
    def on_cancel(self):
        nps.notify_confirm("No changes have been made to configuration",'Exiting',editw=1)
        self.parentApp.setNextForm(None)


class AddSubject(nps.ActionForm):
    def create(self):
        pass
        
    def on_ok(self):
        self.parentApp.switchFormPrevious()
        
    def on_cancel(self):
        nps.notify_confirm("No changes have been made to configuration",'Exiting',editw=1)
        self.parentApp.switchFormPrevious()
       
class AddStation(nps.ActionForm):
    def create(self):
        pass
        
    def on_ok(self):
        self.parentApp.switchFormPrevious()
        
    def on_cancel(self):
        nps.notify_confirm("No changes have been made to configuration",'Exiting',editw=1)
        self.parentApp.switchFormPrevious()
################################################################################
##############################       WIDGETS      ##############################
################################################################################ 

class AddSubjectButtonPress(nps.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm('ADD_SUBJECT')

class AddStationButtonPress(nps.ButtonPress):
    def whenPressed(self):
        self.parent.parentApp.switchForm('ADD_STATION')


################################################################################
################################       APP      ################################
################################################################################

class ConfigureBCore(nps.NPSAppManaged):
    basic_config = []
    
    def onStart(self):
        self.addForm('MAIN',BaseConfigForm,name="Configure your BCore installation")
        self.addForm('SERVER_CONFIG',ConfigureServer,name="Configure your Server")
        self.addForm('CLIENT_CONFIG',ConfigureClient,name="Configure your Client")
        self.addForm('STANDALONE_CONFIG',ConfigureStandAlone,name="Configure StandAlone install")
        self.addForm('ADD_SUBJECT',AddSubject,name="Add a subject")
        self.addForm('ADD_STATION',AddStation,name="Add a station")
        

if __name__ == "__main__":
    App = ConfigureBCore()
    out = App.run()