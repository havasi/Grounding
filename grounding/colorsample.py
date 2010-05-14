from grounding.color_data import make_lab_color_data, lab_to_rgb
from scipy.cluster.vq import kmeans, vq
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

def get_samples(colors, n=8):
    if len(colors) > 200: colors = random.sample(colors, 200)
    color_array = np.array(colors)
    samples = kmeans(color_array, n*3)[0]
    while len(samples) < n:
        color_array += np.random.normal(size=color_array.shape)/100.0
        samples = kmeans(color_array, n*3)[0]
    codes = vq(color_array, samples)[0]
    counts = np.zeros((len(samples),))
    for code in codes:
        counts[code] += 1
    ordered = np.sort(counts)
    median = ordered[-n]
    result = samples[counts >= median]
    assert len(result) >= n
    return result[:n]

def rgb_samples(colors, n=8):
    samples = get_samples(colors, n)
    assert len(samples) == n
    return [lab_to_rgb(s) for s in samples]

def make_html():
    out = open('color_samples.html', 'w')
    out.write(header)
    colordata = make_lab_color_data()
    for colorname in colordata:
        colors = colordata[colorname]
        freq = len(colors)
        if freq >= 8:
            samples = rgb_samples(colors)
            print colorname, samples[0]
            print >> out, "<tr>"
            for sample in samples:
                print >> out, '<td bgcolor="#%02x%02x%02x" width="32">&nbsp;</td>' % sample
            print >> out, '<td>%s (%d)</td>' % (colorname, freq)
            print >> out, '</tr>'
    out.write(footer)
    out.close()

if __name__ == '__main__':
    make_html()

