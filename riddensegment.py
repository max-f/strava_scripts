
class RiddenSegment(object):

    def __init__(self, id, name, segment=None, efforts=None):
        self.id = id
        self.name = name
        self.segment = segment
        self.efforts = efforts

    def get_efforts(self, config, start, end):
        print self.segment.id
        efforts_iterator = config.client.get_segment_efforts(self.segment.id)
                                                             #start_date_local=start, end_date_local=end)
        if not self.efforts:
            self.efforts = []
        for e in efforts_iterator:
            self.efforts.append(e)

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
