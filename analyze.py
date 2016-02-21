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
@click.option('--segment', '-s', type=int, default=0, help='restrict to specific segment by ID')
@pass_config
def segment_ranking(config, order, segment):
    client = config.client
    ridden_segs = read_data(DATAFILE)

    # Restrict to given segment if -s option is specified
    filter_segments(ridden_segs, segment)

    # Crawl leaderboards and times for every segment
    athlete_id = client.get_athlete().id
    leaderboards = collections.defaultdict()
    for k in ridden_segs.keys():
        try:
            leaderboards[k] = client.get_segment_leaderboard(k)
        except:
            continue
    ranks = {k: rank(leaderboards.get(k), athlete_id) for k in ridden_segs.keys()}
    rel_times = {k: relative_time(leaderboards.get(k), ridden_segs[k]) for k in ridden_segs.keys()}

    orderings = {
        'tries' : lambda x: len(x.efforts),
        'elevation': lambda x: x.total_elevation_gain,
        'rank': lambda x: ranks[x.id][0],
        'time': lambda x: rel_times[x.id]
    }
    reverse = {
        'tries': True,
        'elevation': True,
        'rank': False,
        'time': False
    }
    for v in sorted(ridden_segs.values(), key=orderings[order], reverse=reverse[order]):
        rank_string = '%3d/%4d' % (ranks[v.id][0], ranks[v.id][1])
        print (u'Position: %s - Tries: %3d - Elevation gain: %4d - Average time: %4d sec. - '
                'Std. variation in time: %3d sec. - Relative to KOM: %3.1f%% '
               '- Segment: %.30s - ID: %7s' % (rank_string, len(v.efforts), v.total_elevation_gain,
                                               v.avg_time, v.std_time, rel_times[v.id],
                                               v.name, v.id))

    return

def filter_segments(ridden_segs, segment):
    if (segment):
        ridden_segs = {k: v for (k, v) in ridden_segs if k == segment}
    return ridden_segs


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


@cli.command()
@click.argument('athlete_id', type=int)
@pass_config
def get_info(config, athlete_id):
    client = config.client
    infos = collections.defaultdict()
    athlete = client.get_athlete(athlete_id)

    infos['firstname'] = athlete.firstname
    infos['lastname'] = athlete.lastname
    infos['weight'] = athlete.weight

    for (k, v) in infos.items():
        click.echo('%s: %s' % (k, v))


@cli.command()
@click.argument('segmend_id', type=int)
@pass_config
def plot_segment_performance_to_kms(config, segment_id):
    client = config.client
    pass


if __name__ == '__main__':
    cli()

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
