from Criterion import Criterion


class ReceptiveFieldCriterion(Criterion):

    def __init__(self, **kwargs):
        super(ReceptiveFieldCriterion, self).__init__(**kwargs)

    def graduate(self, **kwargs):
        return False