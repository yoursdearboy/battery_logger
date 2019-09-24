#!/usr/bin/env python3
# Script to analyze battery
# requires pandas and bokeh
#   pip install pandas bokeh

import os
import argparse
import datetime
import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show


def load_settings(path):
    settings = {}
    if os.path.isfile(SETTINGS_PATH):
        with open(SETTINGS_PATH) as f:
            for line in f:
                key, value = line.split('=')
                settings[key] = value.strip(' \n\r"\'')
    return settings


SETTINGS_PATH = os.path.join(os.environ.get('HOME', ''), '.battery_logger')
SETTINGS = load_settings(SETTINGS_PATH)


def find_default_logfile_path():
	if 'LOG_PATH' in SETTINGS:
		return SETTINGS['LOG_PATH']
	default_path = os.path.join(os.environ.get('HOME', ''), '.battery.log2')
	if os.path.isfile(default_path):
		return default_path
	return None


parser = argparse.ArgumentParser()
parser.add_argument('logfile', nargs='?', type=argparse.FileType('r'), default=find_default_logfile_path())
parser.add_argument('param', type=str)
args = parser.parse_args()

if args.logfile is None:
    raise Exception("No log file provided")

def read_log_chunk(f):
    acc = []
    empty = False
    for line in f:
        if line.strip():
            acc.append(line.strip())
        else:
            if empty:
                yield acc
                acc = []
                empty = False
            else:
                empty = True


def extract_param(data, param):
    return_value = None
    for line in data:
        content = line.split(' = ', 1)
        if len(content) < 2:
            continue
        key, value = content[0], content[1]
        key = key.strip('"')
        if key == param:
            if return_value is not None:
                print(data)
                raise Exception("Multiple keys matched when extracting \"%s\" param" % param)
            return_value = value
    return return_value


def parse_int(value):
    return int(value) if value is not None else None


df = []
for chunk in read_log_chunk(args.logfile):
    date = datetime.datetime.strptime(chunk[0], '%Y-%m-%d %H:%M:%S')
    data = chunk[1:]
    AvgTimeToEmpty = parse_int(extract_param(data, 'AvgTimeToEmpty')),
    MaxCapacity = parse_int(extract_param(data, 'MaxCapacity'))
    CurrentCapacity = parse_int(extract_param(data, 'CurrentCapacity'))
    CurrentCapacityPercent = CurrentCapacity * 100.0 / MaxCapacity
    Temperature = parse_int(extract_param(data, 'Temperature'))
    df.append(dict(
        date=date,
        AvgTimeToEmpty=AvgTimeToEmpty,
        MaxCapacity=MaxCapacity,
        CurrentCapacity=CurrentCapacity,
        CurrentCapacityPercent=CurrentCapacityPercent,
        Temperature=Temperature
    ))
df = pd.DataFrame(df)

args.logfile.close()

source = ColumnDataSource(df)
p = figure(x_axis_type="datetime", plot_width=800, plot_height=350)
p.yaxis.axis_label = args.param
p.line('date', args.param, source=source)
show(p)
