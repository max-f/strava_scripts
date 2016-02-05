#!/usr/bin/envy python2

import collections
import datetime
import numpy as np

import click
import matplotlib.pyplot as plt
import seaborn as sns
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
@click.argument('order', type=click.Choice(['tries', 'elevation', 'rank', 'time']), default='tries')
@pass_config
def segment_ranking(config, order):
    client = config.client
    ridden_segs = read_data(DATAFILE)

    # Crawl leaderboards and times for every segment
    athlete_id = client.get_athlete().id
    leaderboards = collections.defaultdict()
    for k in ridden_segs.keys():
        try:
            leaderboards[k] = client.get_segment_leaderboard(k)
        except:
            continue
    #leaderboards = {k: client.get_segment_leaderboard(k) for k in ridden_segs.keys()}
    ranks = {k: rank(leaderboards.get(k), athlete_id) for k in ridden_segs.keys()}
    rel_times = {k: relative_time(leaderboards.get(k), ridden_segs[k]) for k in ridden_segs.keys()}

    orderings = {
        'tries' : lambda x: len(x.efforts),
        'elevation': lambda x: x.total_elevation_gain,
        'rank': lambda x: ranks[x.id][0],
        'time': lambda x: rel_times[x.id]
    }
    reversed = {
        'tries': True,
        'elevation': True,
        'rank': False,
        'time': False
    }
    for v in sorted(ridden_segs.values(), key=orderings[order], reverse=reversed[order]):
        rank_string = '%3d/%4d' % (ranks[v.id][0], ranks[v.id][1])
        print (u'Position: %s - Tries: %3d - Elevation gain: %4d - Average time: %4d sec. - '
                'Std. variation in time: %3d sec. - Relative to KOM: %3.1f%% '
               '- Segment: %.30s - ID: %7s' % (rank_string, len(v.efforts), v.total_elevation_gain,
                                               v.avg_time, v.std_time, rel_times[v.id],
                                               v.name, v.id))

    return


def rank(leaderboard, athlete_id):
    if not leaderboard:
        return (0, 0)
    entries = leaderboard.entry_count
    for e in leaderboard.entries:
        if athlete_id == e.athlete_id:
            return (e.rank, entries)


def relative_time(leaderboard, ridden_segment):
    if not leaderboard:
        return 0
    all_times = [e.elapsed_time.total_seconds() for e in leaderboard.entries]
    kom = min(all_times)
    return (ridden_segment.personal_record / kom * 100)


@cli.command()
@click.argument('segment_id', type=int)
@click.option('--distribution', '-d', is_flag=True, default=False)
@pass_config
def plot_times(config, segment_id, distribution):
    """
    Generates a plot to visualize the performance of the current athlete at a specific segment
    in comparison to other athletes.
    :param config: Config object providing API access via security token
    :param segment_id: ID of the strava segment in question
    :param distribution: Whether to plot the time distribution over efforts instead of a boxplot
    :return:
    """
    client = config.client
    ridden_segs = read_data(DATAFILE)

    all_efforts = client.get_segment_efforts(segment_id)
    X = [e.elapsed_time for e in all_efforts]
    X = np.array([datetime.timedelta.total_seconds(x) for x in X])
    Y = np.array([x for x in ridden_segs[segment_id].times])
    if distribution:
        plt.xlabel('Time in seconds')
        sns.distplot(X, hist=False, rug=True)
        sns.distplot(Y, hist=False, rug=True)
        plt.show()
        return
    plt.ylabel('Time in seconds')
    data = np.array([X, Y])
    sns.boxplot(data=data, orient='v')
    plt.show()


if __name__ == '__main__':
    cli()

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
