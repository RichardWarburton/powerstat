#!/usr/bin/env python

# TODO: detect batteries

from time import sleep
from datetime import timedelta

POLL_PERIOD = 10.0

prefix = '/sys/devices/LNXSYSTM:00/device:00/PNP0A08:00/device:09/PNP0C09:00/'
batteries = [prefix + 'PNP0C0A:00/power_supply/BAT0', prefix + 'PNP0C0A:01/power_supply/BAT1']

def read_now(directory):
    return read_file(directory + '/energy_now')
    
def read_full(directory):
    return read_file(directory + '/energy_full')

def read_file(path):
    with open(path, 'r') as the_file:
        return int(the_file.read())

def delta(value):
    (current, last) = value
    return last - current

fulls = map(read_full, batteries)
last = None

while True:
    current = map(read_now, batteries)
    if last:
        deltas = map(delta, zip(current, last))
        values = filter(lambda x: x > 0, deltas)
        if values:
            total = float(sum(current))
            rate = float(values[0]) / POLL_PERIOD
            print str(timedelta(seconds = total / rate))
    last = current
    sleep(POLL_PERIOD)

