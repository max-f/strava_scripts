#!/usr/bin/envy python2

import datetime

import click
import matplotlib.pyplot as plt
from stravalib.client import Client

import riddensegment

class Config(object):

    def __init__(self):
        self.client = Client()

pass_config= click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.argument('token', type=click.File('r'))
@pass_config
def cli(config, token):
    """Script to analyze the user's performance on a given strava segment.
    Using the python strava library by hozn."""
    client = config.client
    access_token = token.read().replace('\n', '')
    client.access_token = access_token


@cli.command()
@click.option('--friend_id', type=int, help='Friend ID to compare the segments'
              ' with')
@pass_config
def segment_ranking(config, friend_id):
    client = config.client
    # test
    b = datetime.datetime(2015, 8, 10, 0, 0, 0)
    my_activities = client.get_activities(before=b, limit=2) # TODO: remove limit?!
    # Have to get all activities a 2nd time individually _with_ annotated
    # segment efforts
    activity_ids = [a.id if a.type == unicode('Ride') else 0 for a in
                    my_activities]
    activities_complete = [client.get_activity(id, include_all_efforts=True) for id in activity_ids]
    segments = {}
    for a in activities_complete:
        for effort in a.segment_efforts:
            try:
                segments[effort.segment.id].efforts = segments[effort.segment.id].efforts + 1
            except KeyError:
                segments[effort.segment.id] = riddensegment.RiddenSegment(effort.segment.id,
                                                                          effort.segment.name,
                                                                          effort.segment.athlete_count)
    for v in sorted(segments.values(), key=lambda v: v.efforts, reverse=True):
        print u'Tried {0} {1} times. Overall {2} athletes '
        'recorded'.format(v.name, v.efforts, v.athlete_count)
    return


@click.command()
@click.option('--graph', is_flag=True, help='Show time distribution graph')
@pass_config
def plot(config):
    return
    """
    segment_id = 5071475 # fechinger berg komplett
    fechinger_berg = client.get_segment(segment_id)
    print('{0} athletes have ridden this segment'.format(fechinger_berg.athlete_count))
    efforts = client.get_segment_efforts(segment_id)
    X = [x.elapsed_time for x in efforts]
    X = [datetime.timedelta.total_seconds(x) for x in X]
    print(len(X))
    print(X[0])
    #sns.distplot(X)
    plt.show()
    """

if __name__ == '__main__':
    cli()

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
