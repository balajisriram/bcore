import time
from verlib import NormalizedVersion as Ver
import os
import pickle
from bcore import get_base_path

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
    _subject_changed = False
    def __init__(self, subject_id, **kwargs):
        """
                Call as follows::
                subject(subjectID='demo')
                subjectID               - MANDATORY
                protocols               - EMPTY
        """
        self.ver = Ver('0.0.3')
        self.subject_id = subject_id
        self._protocol = []
        self._session_manager = []
        self.creation_date = time.time()
        self.iacuc_protocol_id = ''
        if 'reward' in kwargs:
            self._reward = kwargs['reward']
        else:
            self._reward = 0
        if 'timeout' in kwargs:
            self._timeout = kwargs['timeout']
        else:
            self._timeout = 0
        if 'iacuc_protocol_id' in kwargs:
            self.iacuc_protocol_id = kwargs['iacuc_protocol_id']

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


    def __init__(self, subject_id, gender, birth_date, strain, gene_bkgd, **kwargs):
        self.ver = Ver('0.0.1')

        super(Mouse, self).__init__(subject_id , **kwargs)
        self.gender = gender
        self.birth_date = birth_date
        self.strain = strain
        self.gene_bkgd = gene_bkgd
        self.manipulation = []

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


class DefaultMouse(Mouse):

    def __init__(self):
        self.ver = Ver('0.0.1')
        super(DefaultMouse, self).__init__(subject_id='demoMouse',gender='Unknown',
                                          birth_date='',strain='C57BL/6J',gene_bkgd='WT')

    def __repr__(self):
        return "DefaultMouse with id:%s, rewarded at %s ms and punishment at %s ms" % (self.subject_id, self.reward, self.timeout)



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


    def __init__(self, subject_id, gender, birth_date, strain, gene_bkgd, **kwargs):
        self.ver = Ver('0.0.1')

        super(Rat, self).__init__(subject_id, **kwargs)
        self.gender = gender
        self.birth_date = birth_date
        self.strain = strain
        self.gene_bkgd = gene_bkgd
        self.manipulation = []

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


class DefaultRat(Rat):

    def __init__(self,subject_id='demoRat'):
        self.ver = Ver('0.0.1')

        super(DefaultRat, self).__init__(subject_id=subject_id,gender='Unknown',
                                          birth_date='',strain='Long-Evans',gene_bkgd='WT')

    def __repr__(self):
        return "DefaultRat with id:%s, rewarded at %s ms and punishment at %s ms" % (self.subject_id, self.reward, self.timeout)


class VirtualSubject(Subject):
    """
        VIRTUALSUBJECT has the following attributes
        subjectID                 : string ID sent to SUBJECT
    """


    def __init__(self, subject_id, **kwargs):
        self.ver = Ver('0.0.1')

        super(VirtualSubject, self).__init__(subject_id, **kwargs)

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


class DefaultVirtual(VirtualSubject):

    def __init__(self,subject_id='demo_virtual',**kwargs):
        self.ver = Ver('0.0.1')

        super(DefaultVirtual, self).__init__(subject_id, **kwargs)

    def __repr__(self):
        return "DefaultVirtual with id:%s, rewarded at %s ms and punishment at %s ms" % (self.subject_id, self.reward, self.timeout)


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

    def __init__(self, subject_id, gender, birth_date, first_name, last_name, anonymize=False, **kwargs):
        self.ver = Ver('0.0.1')

        super(Human, self).__init__(subject_id, **kwargs)
        self.gender = gender
        self.birth_date = birth_date
        self.first_name = first_name
        self.last_name = last_name
        self.initials = self.first_name[0] + '.' + self.last_name[0] + '.'
        self.anonymize = anonymize

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


class DefaultHuman(Human):

    def __init__(self):
        self.ver = Ver('0.0.1')

        super(DefaultHuman, self).__init__(subject_id='', birth_date='1970-01-01', first_name='Joe', last_name='Smith',
                                          anonymize=False, gender='Unknown')

def get_subject(inp):
    """
        GET_SUBJECT( {'species':'Mouse',
                      'subject_id':'demo1',
                      'gender':'M',
                      'birth_date':'Aug-21-2018',
                      'strain':'C57BL/6J',
                      'gene_bkgd':'WT',
                      'reward': 50,
                      'timeout': 2000,
                      }
    """
    if inp['species']=='Mouse':
        OBJ = Mouse
    elif inp['species']=='Rat':
        OBJ = Rat
    else:
        NotImplementedError('get_subject() assumes you are creating a mouse or a rat')

    return OBJ(subject_id = inp['subject_id'],
               gender = inp['gender'],
               birth_date = inp['birth_date'],
               strain = inp['strain'],
               gene_bkgd = inp['gene_bkgd'],
               reward = inp['reward'],
               timeout = inp['timeout'],
               )


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
