#!/usr/bin/env python


from time import sleep
from datetime import timedelta
from os import listdir
from os.path import join
import sys

POWER_SUPPLIES = "/sys/class/power_supply/"
DEFAULT_POLL_PERIOD = 1.0
SAMPLES = 10

def detect_batteries():
    batteries = [join(POWER_SUPPLIES, bat) for bat in listdir(POWER_SUPPLIES) if bat.startswith('BAT')]
    if not batteries:
        sys.exit(1)
    
    print "Detected {0} batteries".format(len(batteries))
    return batteries

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

def print_delta(seconds):
    if seconds == 0:
        print "No change"
        return

    if seconds < 0:
        prefix = "Charged in"
    else:
        prefix = "Drained in"
    
    print prefix, str(timedelta(seconds=abs(seconds)))

def update_history(history, new_value):
    history.append(new_value)
    if len(history) > SAMPLES:
        history = history[1:]

def output(history):
    if history:
        seconds = sum(history) / len(history)
        print_delta(seconds)

def main():
    batteries = detect_batteries()
    POLL_PERIOD = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_POLL_PERIOD
    history = []
    fulls = map(read_full, batteries)
    last = None
    
    while True:
        current = map(read_now, batteries)
        if last:
            deltas = map(delta, zip(current, last))
            values = filter(lambda x: x != 0, deltas)
            if values:
                total = float(sum(current))
                rate = float(values[0]) / POLL_PERIOD
                update_history(history, total / rate)

        output(history)
        last = current
        sleep(POLL_PERIOD)

if __name__ == "__main__":
    main()

