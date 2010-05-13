from __future__ import with_statement
import numpy as np
import random
from csc.util.persist import PickleDict
pd = PickleDict('pickle', gzip=False)

def total_distance(array, vec):
    return np.sum(np.sqrt(np.sum((array-vec)**2, axis=1)))

def medianesque(array):
    if len(array) > 1000: array = random.sample(array, 1000)
    array = np.asarray(array)
    distances = [total_distance(array, array[i]) for i in xrange(array.shape[0])]
    return array[np.argmin(distances)]

def get_defaultdata():
    defaultdata = {
        'entries': [],
        'freq': 0,
        'male': 0,
    }
    return defaultdata

def get_colors():
    colors = {}
    with open('grouped_color_data.txt') as inputlines:
        for line in inputlines:
            try:
                colorname, userid, r, g, b, monitor, colorblind, male = line.strip().split('|')
            except ValueError:
                continue
            rgb = [float(r), float(g), float(b)]
            if male == '': male=0
            else: male = int(male)

            if colorname not in colors:
                colors[colorname] = get_defaultdata()
            colordata = colors[colorname]

            colordata['entries'].append(rgb)
            colordata['freq'] += 1
            colordata['male'] += male
    return colors

def median_colors():
    all_colors = get_colors()
    colors = {}
    for color in all_colors:
        colordata = all_colors[color]
        if colordata['freq'] >= 3:
            median_color = medianesque(colordata['entries'])
            manliness = colordata['male'] - (colordata['freq'] * male_ratio)
            colors[color] = {
                'rgb': median_color,
                'freq': colordata['freq'],
            }
            print color, median_color
    return colors

if __name__ == '__main__':
    pd['median_colors'] = median_colors()
