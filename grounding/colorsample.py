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

def euclidean_distance(vec1, vec2):
    return np.sqrt(np.sum((vec1-vec2)**2))

def get_samples(colors, n=8):
    mean = np.median(colors, axis=0)
    if len(colors) > n*4:
        samples = np.array(random.sample(colors, n*4))
    else:
        samples = np.array(colors)
    distances = np.array([euclidean_distance(color, mean) for color in samples])
    order = np.argsort(distances)
    return samples[order][:n]

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
            samples = rgb_samples(colors, 8)
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

