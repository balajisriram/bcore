import datetime
from verlib import NormalizedVersion as Ver
import os
import pickle
from bcore import get_base_path, DATETIME_TO_STR
import importlib

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class Subject(object):
    """
        SUBJECT contains all relevant details about the subject.
                subject_id              : string identifier
                protocol                : protocol object
                session_manager         : session manager
                creation_time           : time
                iacuc_protocol_id      : string Identifier
        Changes::
            Ver 0.0.2 - Added iacuc_protocol_id to the object
            Ver 0.0.3 - Added  _property_changed and made getters and setters
    """
    subject_version = Ver('0.0.3')
    subject_id = ''
    _protocol = []
    _session_manager = []
    creation_time = None
    iacuc_protocol_id = ''
    reward = None
    timeout = None


    _subject_changed = False
    def __init__(self, **kwargs):
        """
                Call as follows::
                subject(subjectID='demo')
                subjectID               - MANDATORY
                protocols               - EMPTY
        """
        if not kwargs:
            self.creation_time = datetime.datetime.now()
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        elif 'subject_id' in kwargs:
            self.subject_id = subject_id
            self.creation_time = datetime.datetime.now()
        else:
            pass

    def load_from_dict(self,data)
        self.subject_version = Ver(data['subject_version'])
        self.subject_id = data['subject_id']
        self.creation_time = datetime.datetime.strptime(data['creation_time'],DATETIME_TO_STR)
        self.iacuc_protocol_id = data['iacuc_protocol_id']
        self.reward = data['reward']
        self.timeout = data['timeout']

        prot_class = data['protocol']['class_name']
        prot_data = data['protocol']['protocol_data']
        P = importlib.import_module(prot_class)
        self.protocol = P(data=prot_data)

        sessmgr_class = data['session_manager']['class_name']
        sessmgr_data = data['session_manager']['sessmgr_data']
        SM = importlib.import_module(sessmgr_class)
        self.session_manager = SM(data=sessmgr_data)
        return self

    def save_to_dict(self):
        data = dict()
        data['subject_version'] = self.subject_version.__str__()
        data['subject_id'] = self.subject_id
        data['creation_date'] = datetime.datetime.strftime(self.creation_time,DATETIME_TO_STR)
        data['iacuc_protocol_id'] = self.iacuc_protocol_id
        data['reward'] = self.reward
        data['timeout'] = self.timeout

        p = dict()
        #p['class_name'] = '{0}.{1}'.format(self.protocol.__class__.__module__,self.protocol.__class__.__name__)
        data['protocol'] = self.protocol.save_to_dict()
        #p['protocol_data'] = self.protocol.save_to_dict()
        # need to change how load is run...
        return data


    def __repr__(self):
        return "Subject with id:%s, rewarded at %s ms and punishment at %s ms" % (self.subject_id, self.reward, self.timeout)

    def _clean(self):
        pass

    def __eq__(self, other):
        # if this method is called, then clearly
        return False
        
    ### getters
    @property
    def protocol(self):
        return self._protocol
        
    @property
    def session_manager(self):
        return self._session_manager
    
    @property
    def reward(self):
        return self._reward
        
    @property
    def timeout(self):
        return self._timeout
    
    ### setters
    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        _subject_changed = True
        
    @session_manager.setter
    def session_manager(self, value):
        self._session_manager = value
        _subject_changed = True
    
    @reward.setter
    def reward(self,value):
        self._reward = value
        _subject_changed = True
        
    @timeout.setter
    def timeout(self, value):
        self._timeout = value
        _subject_changed = True

    def add_protocol(self, new_protocol):
        if not self.protocol:
            self.protocol = new_protocol
        else:
            raise ValueError('cannot add new_protocol. protocol is not empty. \
            Maybe you meant replace_protocol()?')

    def add_session_manager(self, new_session_manager):
        if not self.session_manager:
            self.session_manager = new_session_manager
        else:
            raise ValueError('cannot add new_session_manager. session_manager is not empty. \
            Maybe you meant replace_session_manager()?')

    def replace_protocol(self, new_protocol):
        self.protocol = new_protocol

    def replace_session_manager(self, new_session_manager):
        self.session_manager = new_session_manager

    def allowed_genders(self):
        return None

    def allowed_strains(self):
        return None

    def allowed_gene_bkgd(self):
        return None

    def do_trial(self, station, trial_record, compiled_record, quit):
        # Called by station.do_trials()
        if not self.protocol:
            raise ValueError('Protocol Unavailable: cannot run subject without \
            a protocol')

        # new consideration in  protocol and training step
        graduate = False

        # some basic info about the subject
        trial_record['subject_id'] = self.subject_id
        trial_record['subject_version_number'] = self.ver.__str__()

        # figure out the protocol, and the trainingStep details
        trial_record['protocol_name'] = self.protocol.name
        trial_record['protocol_version_number'] = self.protocol.ver.__str__()
        trial_record['current_step'] = self.protocol.current_step
        trial_record['current_step_name'] = self.protocol.step(compiled_record=compiled_record,trial_record=trial_record).name
        trial_record['num_steps'] = self.protocol.num_steps

        current_step = self.protocol.step(compiled_record=compiled_record,trial_record=trial_record)
        trial_record,quit = current_step.do_trial(subject=self, station=station, trial_record=trial_record, compiled_record=compiled_record,quit = quit)
        if trial_record['graduate']:
            trial_record['criterion_met'] = True
            self.protocol.graduate()
        else:
            trial_record['criterion_met'] = False

        return trial_record, quit

    def load_compiled_records(self):
        # location is get_base_path->BCoreData->CompiledTrialRecords->subject_id.compiled_record
        compiled_file_loc = os.path.join(get_base_path(),"BCoreData","SubjectData","CompiledTrialRecords")
        files = [i for i in os.listdir(compiled_file_loc) if \
                 os.path.isfile(os.path.join(compiled_file_loc,i)) and self.subject_id in i]
        print(self.subject_id)
        print(files)
        if len(files)>1:
            RuntimeError("SUBJECT:SUBJECT:LOAD_COMPILED_RECORDS:Too many records")
        elif len(files)==1:
            with open(os.path.join(compiled_file_loc,files[0]),"rb") as f:
                cR = pickle.load(f)
        else:
            cR = None

        return cR

    def save_compiled_records(self, cR):
        # location is get_base_path->BCoreData->SubjectData->CompiledTrialRecords->subject_id.compiled_record
        from BCore import get_base_path
        import os
        import pickle
        compiled_file_loc = os.path.join(get_base_path(), "BCoreData", "SubjectData", "CompiledTrialRecords")
        files = [i for i in os.listdir(compiled_file_loc) if \
                 os.path.isfile(os.path.join(compiled_file_loc, i)) and self.subject_id in i]

        if len(files)>1:
            pass
        elif len(files)==1:
            os.remove(os.path.join(compiled_file_loc,files[0]))
        else:
            pass

        tNum = cR["trial_number"][-1]
        sid = self.subject_id
        cR_name = '{0}.1-{1}.compiled_record'.format(sid,tNum)
        with open(os.path.join(compiled_file_loc,cR_name), "wb") as f:
            pickle.dump(cR,f)

    def save_session_records(self,sR):
        # location is get_base_path->BCoreData->PermanentTrialRecords->subject_id->trialRecord.1-N.session_record
        from BCore import get_base_path
        import os
        import pickle
        session_file_loc = os.path.join(get_base_path(), "BCoreData", "SubjectData", "SessionRecords",self.subject_id)
        if not os.path.exists(session_file_loc):
            os.makedirs(session_file_loc)
        tnum_lo = sR[0]["trial_number"]
        tnum_hi = sR[-1]["trial_number"]

        sR_name = "trialRecords.{0}-{1}.session_record".format(tnum_lo,tnum_hi)
        with open(os.path.join(session_file_loc, sR_name), "wb") as f:
            pickle.dump(sR, f)

class Mouse(Subject):
    """
        MOUSE has the following attributes
        subjectID                 : string ID sent to SUBJECT
        gender                    : 'M'/'F'
        birthDate                 : mm/dd/yyyy
        strain                    : string identifier
        geneBkgd                  : string identifier
        manipulation              : three-ple list
    """
    mouse_version = Ver('0.0.1')
    gender = ''
    birth_date = None
    strain = ''
    gene_bkgd = ''
    manipulation = []

    def __init__(self, , **kwargs):
        super(Mouse,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self,data):
        self.mouse_version = Ver(data['mouse_version'])
        self.gender = data['gender']
        self.birth_date = datetime.datetime.strptime(data['birth_date'], DATETIME_TO_STR)
        self.strain = data['strain']
        self.gene_bkgd = data['gene_bkgd']
        self.manipulation = data['manipulation']
        return self

    def save_to_dict(self):
        data = super(Mouse,self).save_to_dict()
        data['mouse_version'] = self.mouse_version.__str__()
        data['gender'] = self.gender
        data['birth_date'] = datetime.datetime.strftime(self.birth_date, DATETIME_TO_STR)
        data['strain'] = self.strain
        data['gene_bkgd'] = self.gene_bkgd
        data['manipulation'] = self.manipulation
        return data

    def __repr__(self):
        return "Mouse with id:%s, rewarded at %s ms and punishment at %s ms" % (self.subject_id, self.reward, self.timeout)

    def __eq__(self, other):
        if isinstance(other, Mouse) and (self.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(self):
        return ['Male', 'Female', 'Unknown']

    def allowed_strains(self):
        return ['C57BL/6J', '129S1/SvlmJ', 'BALB/c']

    def allowed_gene_bkgd(self):
        return ['WT', 'Pvalb-cre', 'Pvalb-COP4-EYFP', 'Somst-cre']

class Rat(Subject):
    """
        RAT has the following attributes
        subjectID                 : string ID sent to SUBJECT
        gender                    : 'M'/'F'
        birthDate                 : mm/dd/yyyy
        strain                    : string identifier
        geneBkgd                  : string identifier
        manipulation              : three-ple list
    """

    rat_version = Ver('0.0.1')
    gender = ''
    birth_date = None
    strain = ''
    gene_bkgd = ''
    manipulation = []

    def __init__(self, **kwargs):
        super(Rat,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self, data):
        self.rat_version = Ver(data['rat_version'])
        self.gender = data['gender']
        self.birth_date = datetime.datetime.strptime(data['birth_date'])
        self.strain = data['strain']
        self.gene_bkgd = data['gene_bkgd']
        self.manipulation = data['manipulation']
        return self

    def save_to_dict(self):
        data = super(Rat,self).save_to_dict()
        data['rat_version'] = self.rat_version.__str__()
        data['gender'] = self.gender
        data['birth_date'] = datetime.datetime.strftime(self.birth_date, DATETIME_TO_STR)
        data['strain'] = self.strain
        data['gene_bkgd'] = self.gene_bkgd
        data['manipulation'] = self.manipulation
        return data

    def __repr__(self):
        return "Rat with id:%s, rewarded at %s ms and punishment at %s ms" % (self.subject_id, self.reward, self.timeout)

    def __eq__(self, other):
        if isinstance(other, Rat) and (self.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(self):
        return ['Male', 'Female', 'Unknown']

    def allowed_strains(self):
        return ['Wistar', 'Sprague-Dawley', 'Long-Evans']

    def allowed_gene_bkgd(self):
        return ['WT']

class VirtualSubject(Subject):
    """
        VIRTUALSUBJECT has the following attributes
        subjectID                 : string ID sent to SUBJECT
    """
    virtual_version = Ver('0.0.1')
    def __init__(self, **kwargs):
        super(VirtualSubject,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self, data):
        self.virtual_version = Ver(data['virtual_version'])
        return self

    def save_to_dict(self):
        data = super(VirtualSubject,self).save_to_dict()
        return data

    def __repr__(self):
        return "VirtualSubject with id:%s, rewarded at %s ms and punishment at %s ms" % (self.subject_id, self.reward, self.timeout)

    def __eq__(self, other):
        if isinstance(other, VirtualSubject) and (self.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(self):
        return None

    def allowed_strains(self):
        return None

    def allowed_gene_bkgd(self):
        return None

class Human(Subject):
    """
        HUMAN has the following attributes
        subjectID                 : string ID sent to SUBJECT
        gender                    : 'M'/'F'/'O'/'NA'
        birthDate                 : mm/dd/yyyy
        firstName                 : string ID
        lastName                  : string ID
        initials                  : f.l.
        anonymize                 : True/False
    """

    human_version = Ver('0.0.1')
    gender = ''
    birth_date = None
    firt_name = ''
    last_name = ''
    initials = ''

    def __init__(self, **kwargs):
        super(Human,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self, data):
        self.human_version = Ver(data['human_version'])
        self.gender = data['gender']
        self.birth_date = datetime.datetime.strptime(data['birth_date'])
        self.firt_name = data['firt_name']
        self.last_name = data['last_name']
        self.anonymize = data['anonymize']
        return self

    def save_to_dict(self):
        data = super(Human,self).save_to_dict()
        data['human_version'] = self.human_version.__str__()
        data['gender'] = self.gender
        data['birth_date'] = datetime.datetime.strftime(self.birth_date, DATETIME_TO_STR)
        data['firt_name'] = self.firt_name
        data['last_name'] = self.last_name
        data['anonymize'] = self.anonymize
        return data

    def __repr__(self):
        return "Human (%s), rewarded at %s ms and punishment at %s ms" % (self.initials, self.reward, self.timeout)

    def __eq__(self, other):
        if isinstance(other, Human) and (self.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(self):
        return ['Male', 'Female', 'Other', 'Unknown']

    def allowed_strains(self):
        return None

    def allowed_gene_bkgd(self):
        return None

if __name__ == '__main__':
    print('Will create an example MOUSE for comparison')
    a = Mouse(
        subjectID='999',
        gender='M',
        birthDate='02/10/2014',
        strain='c57bl/6j',
        geneBkgd='PV-cre')
    print(('MOUSE is a Mouse? ' + str(isinstance(a, Mouse))))
    print(('MOUSE is a Rat? ' + str(isinstance(a, Rat))))
    print(('MOUSE is a Subject? ' + str(isinstance(a, Subject))))
