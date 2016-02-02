#!/usr/bin/envy python2

import datetime
import numpy as np

import click
#import matplotlib.pyplot as plt

from manage_data import Config, read_data

pass_config = click.make_pass_decorator(Config, ensure=True)

DATAFILE = 'data'

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
@click.option('--time', is_flag=True, help='Sort segments by time relative '
              'to the other athletes. Default is sorting by effort count.')
@pass_config
def segment_ranking(config, time):
    ridden_segs = read_data(DATAFILE)
    for v in sorted(ridden_segs.values(), key=lambda v: len(v.efforts), reverse=True):
        times = [e.elapsed_time.total_seconds() for e in v.efforts]
        avg_time = np.mean(times)
        std_dev = np.std(times)
        print (u'Tries: %3d - Elevation gain: %4d - Average time: %4d sec. - '
        'Std. variation in time: %3d sec. - Segment: %.30s' % (len(v.efforts), v.total_elevation_gain, avg_time, std_dev,
                                                         v.name))
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
