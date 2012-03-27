from grounding.color_data import make_lab_color_data, lab_to_rgb
from collections import defaultdict
import numpy as np
import random

header = """
<!doctype html>
<html><body bgcolor="#999999">
<table>
"""

footer = """
</table>
</body></html>
"""

def euclidean_distance(vec1, vec2):
    if isinstance(vec1, tuple):
        vec1 = np.array(vec1)
    if isinstance(vec2, tuple):
        vec2 = np.array(vec2)
    return np.sqrt(np.sum((vec1-vec2)**2))

def elect_stv(candidates, ballots, nwinners):
    winners = []
    running = set(candidates)
    quota = int(len(ballots) / (nwinners+1.0)) + 1

    while len(winners) < nwinners:
        if len(running) == 0:
            break
        totals = defaultdict(int)
        for ballot in ballots:
            for vote in ballot:
                if vote in running:
                    totals[vote] += 1
                    break
        total_votes = totals.items()
        total_votes.sort(key=lambda x: -x[1])
        elected_one = False
        for candidate, votes in total_votes:
            if votes >= quota:
                winners.append(candidate)
                running.remove(candidate)
                elected_one = True
                break
        if not elected_one:
            loser = total_votes[-1][0]
            running.remove(loser)

    assert len(winners) <= nwinners

    return winners

def elect_samples(colors, n=8):
    if len(colors) > 1000:
        samples = random.sample(colors, n*5)
        colors = random.sample(colors, 1000)
    elif len(colors) > n*5:
        samples = random.sample(colors, n*5)
        assert len(samples) == n*5
    else:
        samples = colors
    votes = []

    for color in colors:
        ratings = []
        for candidate in samples:
            ratings.append((euclidean_distance(color, candidate),
                tuple(candidate)))
        ratings.sort()
        vote = [r[1] for r in ratings]
        votes.append(vote)

    winners = elect_stv(samples, votes, n)
    return [lab_to_rgb(x) for x in winners]

def make_html():
    out = open('color_samples.html', 'w')
    out.write(header)
    colordata = make_lab_color_data()
    for colorname in colordata:
        colors = colordata[colorname]
        freq = len(colors)
        if freq >= 8:
            samples = elect_samples(colors, 8)
            if len(samples) == 8:
                print colorname, samples
                print >> out, "<tr>"
                for sample in samples:
                    print >> out, '<td bgcolor="#%02x%02x%02x" width="32">&nbsp;</td>' % sample
                print >> out, '<td>%s (%d)</td>' % (colorname, freq)
                print >> out, '</tr>'
    out.write(footer)
    out.close()

if __name__ == '__main__':
    make_html()

