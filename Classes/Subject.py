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

    def do_trial(sub, tR, **kwargs):
        # Called by station.doTrials()
        if not sub.protocol:
            raise ValueError('Protocol Unavailable: cannot run subject without \
            a protocol')

        # new consideration in  protocol and training step
        graduate = False
        kwargs['graduate'] = graduate
        kwargs['subject'] = sub

        # figure out the protocol, and the trainingStep details
        tR.protocol_name = sub.protocol.name
        tR.protocol_version_number = sub.protocol.ver
        tR.current_step = sub.protocol.current_step
        tR.current_step_name = sub.protocol.step().name
        tR.numSteps = sub.protocol.numSteps()

        current_step = sub.protocol.step()
        tR = current_step.do_trial(tR,**kwargs)

        if kwargs['graduate']:
            tR.criterionMet = True
            sub.protocol.graduate()

        return tR


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
