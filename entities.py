#!/usr/bin/env python

import numpy as np

class RiddenSegment(object):
    """
    Class represents a specific segment I have ridden at least once. Efforts only include my own ones.
    """

    def __init__(self, id, name, distance, total_elevation_gain, avg_grade, efforts=None):
        self.id = id
        self.name = name
        self.distance = distance
        self.total_elevation_gain = total_elevation_gain
        self.avg_grade = avg_grade
        self.efforts = efforts

    @property
    def times(self):
        return [e.elapsed_time.total_seconds() for e in self.efforts]

    @property
    def avg_time(self):
        return np.mean(self.times)

    @property
    def std_time(self):
        return np.std(self.times)

    @property
    def personal_record(self):
        return min(self.times)


class Effort(object):

    def __init__(self, date, segment_id, elapsed_time, avg_heartrate, avg_watts):
        self.date = date
        self.segment_id = segment_id
        self.elapsed_time = elapsed_time
        self.avg_heartrate = avg_heartrate
        self.avg_watts = avg_watts

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
