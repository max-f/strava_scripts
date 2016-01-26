
class RiddenSegment(object):

    def __init__(self, id, name, effort_times=None, athlete_count=0,
                 segment=None):
        self.id = id
        self.name = name
        self.efforts = 1
        if effort_times is None:
            self.effort_times = []
        else:
            self.effort_times = effort_times
        self.athlete_count = athlete_count
        self.segment = segment

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
