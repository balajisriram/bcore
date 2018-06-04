import time
from verlib import NormalizedVersion as Ver

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
                subjectID               : string identifier
                protocol                : protocol object
    """
    ver = Ver('0.0.1')

    def __init__(sub, subject_id, **kwargs):
        """
                Call as follows::
                subject(subjectID='demo')
                subjectID               - MANDATORY
                protocols               - EMPTY
        """
        sub.subject_id = subject_id
        sub.protocol = []
        sub.session_manager = []
        sub.creation_date = time.time()
        sub._current_trial_num = 0

    def _clean(self):
        pass

    def __eq__(sub, other):
        # if this method is called, then clearly
        return False

    def add_protocol(sub, new_protocol):
        if not sub.protocol:
            sub.protocol = new_protocol
        else:
            raise ValueError('cannot add new_protocol. protocol is not empty. \
            Maybe you meant replace_protocol()?')

    def add_session_manager(sub, new_session_manager):
        if not sub.session_manager:
            sub.session_manager = new_session_manager
        else:
            raise ValueError('cannot add new_session_manager. session_manager is not empty. \
            Maybe you meant replace_session_manager()?')

    def replace_protocol(sub, new_protocol):
        sub.protocol = new_protocol

    def replace_session_manager(sub, new_session_manager):
        sub.session_manager = new_session_manager

    def allowed_genders(sub):
        return None

    def allowed_strains(sub):
        return None

    def allowed_gene_bkgd(sub):
        return None

    def do_trial(sub, station, trial_record, compiled_record, quit):
        # Called by station.do_trials()
        if not sub.protocol:
            raise ValueError('Protocol Unavailable: cannot run subject without \
            a protocol')

        # new consideration in  protocol and training step
        graduate = False
        
        # figure out the protocol, and the trainingStep details
        trial_record['protocol_name'] = sub.protocol.name
        trial_record['protocol_version_number'] = sub.protocol.ver
        trial_record['current_step'] = sub.protocol.current_step
        import pdb
        pdb.set_trace()
        trial_record['current_step_name'] = sub.protocol.step().name
        trial_record['numSteps'] = sub.protocol.numSteps()

        current_step = sub.protocol.step()
        trial_record, quit = current_step.do_trial(trial_record,subject=sub, station=station, 
                   trial_record=trial_record, compiled_record=compiled_record, quit=quit)

        if kwargs['graduate']:
            trial_record.criterionMet = True
            sub.protocol.graduate()

        return trial_record, quit

    def load_compiled_records(self):
        # location is get_base_directory->BCoreData->CompiledTrialRecords->subject_id.compiled_record
        from BCore import get_base_directory
        import os
        import pickle
        compiled_file_loc = os.path.join(get_base_directory(),"BCoreData","SubjectData","CompiledTrialRecords")
        files = [i for i in os.listdir(compiled_file_loc) if \
                 os.path.isfile(os.path.join(compiled_file_loc,i)) and self.subject_id in i]
        if len(files)>1:
            RuntimeError("SUBJECT:SUBJECT:LOAD_COMPILED_RECORDS:Too many records")
        elif len(files)==1:
            with open(os.path.join(compiled_file_loc,files[0]),"rb") as f:
                cR = pickle.load(f)
        else:
            cR = None

        return cR

    def save_compiled_records(self, cR):
        # location is get_base_directory->BCoreData->CompiledTrialRecords->subject_id.compiled_record
        from BCore import get_base_directory
        import os
        import pickle
        compiled_file_loc = os.path.join(get_base_directory(), "BCoreData", "CompiledTrialRecords")
        files = [i for i in os.listdir(compiled_file_loc) if \
                 os.path.isfile(os.path.join(compiled_file_loc, i)) and self.subject_id in i]

        if len(files)>1:
            pass
        elif len(files)==1:
            os.remove(os.path.join(compiled_file_loc,files[0]))
        else:
            pass

        tNum = cR[-1]["trialNumber"]
        sid = self.subject_id
        cR_name = '{0}.1-{1}.compiled_record'.format(sid,tNum)
        with open(os.path.join(compiled_file_loc,cR_name), "wb") as f:
            pickle.dump(cR,f)

    def save_session_records(self,sR):
        # location is get_base_directory->BCoreData->PermanentTrialRecords->subject_id->trialRecord.1-N.session_record
        from BCore import get_base_directory
        import os
        import pickle
        session_file_loc = os.path.join(get_base_directory(), "BCoreData", "PermanentTrialRecords",self.subject_id)
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

    ver = Ver('0.0.1')

    def __init__(sub, subject_id, gender, birth_date, strain, gene_bkgd, **kwargs):
        super(Mouse, sub).__init__(subject_id , **kwargs)
        sub.gender = gender
        sub.birth_date = birth_date
        sub.strain = strain
        sub.gene_bkgd = gene_bkgd
        sub.manipulation = []

    def __eq__(sub, other):
        if isinstance(other, Mouse) and (sub.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(sub):
        return ['Male', 'Female', 'Unknown']

    def allowed_strains(sub):
        return ['C57BL/6J', '129S1/SvlmJ', 'BALB/c']

    def allowed_gene_bkgd(sub):
        return ['WT', 'Pvalb-cre', 'Pvalb-COP4-EYFP', 'Somst-cre']


class DefaultMouse(Mouse):
    ver = Ver('0.0.1')

    def __init__(sub):
        super(DefaultMouse, sub).__init__(subject_id='demoMouse',gender='Unknown',
                                          birth_date='',strain='C57BL/6J',gene_bkgd='WT')


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

    ver = Ver('0.0.1')

    def __init__(sub, subject_id, gender, birth_date, strain, gene_bkgd, **kwargs):
        super(Rat, sub).__init__(subject_id, **kwargs)
        sub.gender = gender
        sub.birth_date = birth_date
        sub.strain = strain
        sub.gene_bkgd = gene_bkgd
        sub.manipulation = []

    def __eq__(sub, other):
        if isinstance(other, Rat) and (sub.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(sub):
        return ['Male', 'Female', 'Unknown']

    def allowed_strains(sub):
        return ['Wistar', 'Sprague-Dawley', 'Long-Evans']

    def allowed_gene_bkgd(sub):
        return ['WT']


class DefaultRat(Rat):
    ver = Ver('0.0.1')

    def __init__(sub,subject_id='demoRat'):
        super(DefaultRat, sub).__init__(subject_id=subject_id,gender='Unknown',
                                          birth_date='',strain='Long-Evans',gene_bkgd='WT')


class VirtualSubject(Subject):
    """
        VIRTUALSUBJECT has the following attributes
        subjectID                 : string ID sent to SUBJECT
    """

    ver = Ver('0.0.1')

    def __init__(sub, subject_id, **kwargs):
        super(VirtualSubject, sub).__init__(subject_id, **kwargs)

    def __eq__(sub, other):
        if isinstance(other, VirtualSubject) and (sub.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(sub):
        return None

    def allowed_strains(sub):
        return None

    def allowed_gene_bkgd(sub):
        return None


class DefaultVirtual(VirtualSubject):
    ver = Ver('0.0.1')

    def __init__(sub,subject_id='demo_virtual'):
        super(DefaultVirtual, sub).__init__(subject_id)


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
    ver = Ver('0.0.1')

    def __init__(sub, subject_id, gender, birth_date, first_name, last_name, anonymize=False, **kwargs):
        super(Human, sub).__init__(subject_id, **kwargs)
        sub.gender = gender
        sub.birth_date = birth_date
        sub.first_name = first_name
        sub.last_name = last_name
        sub.initials = sub.first_name[0] + '.' + sub.last_name[0] + '.'
        sub.anonymize = anonymize

    def __eq__(sub, other):
        if isinstance(other, Human) and (sub.subject_id == other.subject_id):
            return True
        else:
            return False

    def allowed_genders(sub):
        return ['Male', 'Female', 'Other', 'Unknown']

    def allowed_strains(sub):
        return None

    def allowed_gene_bkgd(sub):
        return None


class DefaultHuman(Human):
    ver = Ver('0.0.1')

    def __init__(sub):
        super(DefaultHuman, sub).__init__(subject_id='', birth_date='1970-01-01', first_name='Joe', last_name='Smith',
                                          anonymize=False, gender='Unknown')


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
