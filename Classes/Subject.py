import time


class Subject(object):
    """
        SUBJECT contains all relevant details about the subject.
                subjectID               : string identifier
                protocol                : protocol object
    """

    def __init__(self, **kwargs):
        """
                Call as follows::
                subject(subjectID='demo')
                subjectID               - MANDATORY
                protocols               - EMPTY
        """
        self.subjectID = kwargs['subjectID']
        self.protocol = []
        self.creationDate = time.time()

    def __eq__(self, other):
        # if this method is called, then clearly
        return False

    def addProtocol(self, newProtocol):
        self.protocol.append(newProtocol)

    def allowedGenders(self):
        return None

    def allowedStrains(self):
        return None

    def allowedGeneBkgd(self):
        return None


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

    def __init__(self, **kwargs):
        super(Mouse, self).__init__(subjectID=kwargs['subjectID'])
        self.gender = kwargs['gender']
        self.birthDate = kwargs['birthDate']
        self.strain = kwargs['strain']
        self.geneBkgd = kwargs['geneBkgd']
        self.manipulation = []

    def __eq__(self, other):
        if isinstance(other, Mouse) and (self.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(self):
        return ['Male', 'Female']

    def allowedStrains(self):
        return ['C57BL/6J', '129S1/SvlmJ', 'BALB/c']

    def allowedGeneBkgd(self):
        return ['WT', 'Pvalb-cre', 'Pvalb-COP4-EYFP', 'Somst-cre']


class DefaultMouse(Mouse):
    def __init__(self):
        pass


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

    def __init__(self, **kwargs):
        super(Rat, self).__init__(subjectID=kwargs['subjectID'])
        self.gender = kwargs['gender']
        self.birthDate = kwargs['birthDate']
        self.strain = kwargs['strain']
        self.geneBkgd = kwargs['geneBkgd']
        self.manipulation = []

    def __eq__(self, other):
        if isinstance(other, Rat) and (self.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(self):
        return ['Male', 'Female']

    def allowedStrains(self):
        return ['Wistar', 'Sprague-Dawley', 'Long-Evans']

    def allowedGeneBkgd(self):
        return ['WT']


class DefaultRat(Rat):
    def __init__(self):
        pass


class Virtual(Subject):
    """
        VIRTUAL has the following attributes
        subjectID                 : string ID sent to SUBJECT
    """

    def __init__(self, **kwargs):
        super(Virtual, self).__init__(subjectID=kwargs['subjectID'])

    def __eq__(self, other):
        if isinstance(other, Virtual) and (self.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(self):
        return None

    def allowedStrains(self):
        return None

    def allowedGeneBkgd(self):
        return None


class DefaultVirtual(Virtual):
    def __init__(self):
        pass


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

    def __init__(self, **kwargs):
        super(Human, self).__init__(subjectID=kwargs['subjectID'])
        self.gender = kwargs['gender']
        self.birthDate = kwargs['birthDate']
        self.firstName = kwargs['firstName']
        self.lastName = kwargs['lastName']
        self.initials = self.firstName[0] + '.' + self.lastName[0] + '.'
        self.anonymize = False

    def __eq__(self, other):
        if isinstance(other, Human) and (self.subjectID == other.subjectID):
            return True
        else:
            return False

    def allowedGenders(self):
        return ['Male', 'Female', 'Other', 'NA']

    def allowedStrains(self):
        return None

    def allowedGeneBkgd(self):
        return None


class DefaultHuman(Human):
    def __init__(self):
        pass


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
