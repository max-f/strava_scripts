#!/usr/bin/env python
import copy
import datetime
import time
import cPickle

import click
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
    """Script to manage specific strava data of the user for analyzing purposes while minimizing API calls.
    Using the python strava library by hozn."""
    client = config.client
    access_token = token.read().replace('\n', '')
    client.access_token = access_token

@cli.command()
@pass_config
def init(config):
    client = config.client
    d = datetime.datetime(year=2015, month=7, day=10)
    activities = client.get_activities(before=d, limit=2)
    ridden_segs = {}
    sync_data(config, activities, ridden_segs)

def sync_data(config, activities, ridden_segs):
    activity_ids = [a.id for a in activities if a.type == unicode('Ride')]
    click.echo('%4d rides not synced' % len(activity_ids))
    value = click.prompt('How many of those rides should be synced this time?', type=int)
    activity_ids = activity_ids[:value]
    ridden_segs = {}
    for chunk in list_chunks(activity_ids, 2):
        ridden_segs = crawl_activities(config, chunk, ridden_segs)
        # Prevent too many API requests in short time
        time.sleep(0)
    click.echo('-- DONE: %3d rides synced --' % len(activity_ids))
    with open('data', 'wb') as f:
        cPickle.dump(ridden_segs, f)

def crawl_activities(config, activity_ids, ridden_segs):
    client = config.client
    # Get all activities a 2nd time individually _with_ annotated
    # segment efforts
    activities_complete = [client.get_activity(id, include_all_efforts=True) for id in activity_ids]
    for a in activities_complete:
        for effort in a.segment_efforts:
            s = client.get_segment(effort.segment.id)
            if s.id not in ridden_segs:
                ridden_segs[s.id] = riddensegment.RiddenSegment(s.id, s.name, s, [effort])
            else:
                ridden_segs[s.id].efforts.append(effort)

    return ridden_segs

def list_chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def unique_elements(l, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for e in l:
        marker = idfun(e)
        if marker in seen: continue
        seen[marker] = 1
        result.append(e)
    return result

@cli.command()
@pass_config
def update(config):
    pass

def read(filename):
    with open(filename, 'rb') as f:
        d = cPickle.load(f)
    return d


if __name__ == '__main__':
    cli()

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
