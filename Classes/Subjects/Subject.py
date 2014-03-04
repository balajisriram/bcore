import time
from verlib import NormalizedVersion as Ver


class Subject(object):
    """
        SUBJECT contains all relevant details about the subject.
                subjectID               : string identifier
                protocol                : protocol object
    """
    ver = Ver('0.0.1')

    def __init__(sub, **kwargs):
        """
                Call as follows::
                subject(subjectID='demo')
                subjectID               - MANDATORY
                protocols               - EMPTY
        """
        sub.subjectID = kwargs['subjectID']
        sub.protocol = []
        sub.creationDate = time.time()

    def __eq__(sub, other):
        # if this method is called, then clearly
        return False

    def addProtocol(sub, newProtocol):
        if not sub.protocol:
            sub.protocol = newProtocol
        else:
            raise ValueError('cannot add newProtocol. protocol is not empty. \
            Maybe you meant replaceProtocol()?')

    def replaceProtocol(sub, newProtocol):
        sub.protocol = newProtocol

    def allowedGenders(sub):
        return None

    def allowedStrains(sub):
        return None

    def allowedGeneBkgd(sub):
        return None

    def doTrial(sub, **kwargs):
        if not sub.protocol:
            raise ValueError('Protocol Unavailable: cannot run subject without \
            a protocol')
        tR = kwargs['trialRecord']
        Quit = kwargs['quit']
        
        # new consideration in  protocol and training step 
        Graduate = False
        kwargs['graduate'] = Graduate
        
        # figure out the protocol, and the trainingStep details
        tR.protocol = sub.protocol.name
        tR.currentStep = sub.protocol.currentStep
        tR.numSteps = sub.protocol.numSteps()
        currentStep = sub.protocol.step()
        
        currentStep.doTrial(**kwargs)
        
        if kwargs['graduate']:
            sub.protocol.graduate()

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

    def __init__(sub, **kwargs):
        super(Mouse, sub).__init__(**kwargs)
        sub.gender = kwargs['gender']
        sub.birthDate = kwargs['birthDate']
        sub.strain = kwargs['strain']
        sub.geneBkgd = kwargs['geneBkgd']
        sub.manipulation = []

    def __eq__(sub, other):
        if isinstance(other, Mouse) and (sub.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(sub):
        return ['Male', 'Female']

    def allowedStrains(sub):
        return ['C57BL/6J', '129S1/SvlmJ', 'BALB/c']

    def allowedGeneBkgd(sub):
        return ['WT', 'Pvalb-cre', 'Pvalb-COP4-EYFP', 'Somst-cre']


class DefaultMouse(Mouse):
    def __init__(sub):
        pass

    def createSubject(sub, **kwargs):
        return Mouse(**kwargs)


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

    def __init__(sub, **kwargs):
        super(Rat, sub).__init__(subjectID=kwargs['subjectID'])
        sub.gender = kwargs['gender']
        sub.birthDate = kwargs['birthDate']
        sub.strain = kwargs['strain']
        sub.geneBkgd = kwargs['geneBkgd']
        sub.manipulation = []

    def __eq__(sub, other):
        if isinstance(other, Rat) and (sub.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(sub):
        return ['Male', 'Female']

    def allowedStrains(sub):
        return ['Wistar', 'Sprague-Dawley', 'Long-Evans']

    def allowedGeneBkgd(sub):
        return ['WT']


class DefaultRat(Rat):
    def __init__(sub):
        pass

    def createSubject(sub, **kwargs):
        return Rat(**kwargs)


class Virtual(Subject):
    """
        VIRTUAL has the following attributes
        subjectID                 : string ID sent to SUBJECT
    """

    def __init__(sub, **kwargs):
        super(Virtual, sub).__init__(**kwargs)

    def __eq__(sub, other):
        if isinstance(other, Virtual) and (sub.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(sub):
        return None

    def allowedStrains(sub):
        return None

    def allowedGeneBkgd(sub):
        return None


class DefaultVirtual(Virtual):
    def __init__(sub):
        pass

    def createSubject(sub, **kwargs):
        return Virtual(**kwargs)


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

    def __init__(sub, **kwargs):
        super(Human, sub).__init__(**kwargs)
        sub.gender = kwargs['gender']
        sub.birthDate = kwargs['birthDate']
        sub.firstName = kwargs['firstName']
        sub.lastName = kwargs['lastName']
        sub.initials = sub.firstName[0] + '.' + sub.lastName[0] + '.'
        sub.anonymize = False

    def __eq__(sub, other):
        if isinstance(other, Human) and (sub.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(sub):
        return ['Male', 'Female', 'Other', 'NA']

    def allowedStrains(sub):
        return None

    def allowedGeneBkgd(sub):
        return None


class DefaultHuman(Human):
    def __init__(sub):
        pass

    def createSubject(sub, **kwargs):
        return Human(**kwargs)


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
    
    b = Mouse(
        subjectID='998',
        gender='M',
        birthDate='02/10/2014',
        strain='c57bl/6j',
        geneBkgd='PV-cre')
        
    c = Mouse(
        subjectID='997',
        gender='M',
        birthDate='02/10/2014',
        strain='c57bl/6j',
        geneBkgd='PV-cre')
    mouselist = [a,b]
    if c in mouselist:
        print 'avail'