from pkg_resources import resource_filename, resource_stream
from collections import defaultdict
from csc.conceptnet4.models import RightFeature, Assertion, Language
from grounding.models import ColorAssertion, NotColorfulAssertion
from csc.util.persist import PickleDict
from csc import divisi2
from grounding.colorizer import Colorizer
from grounding import xkcd_plot
import numpy as np
import logging
import random

log = logging.getLogger('colorizer')
log.setLevel(logging.INFO)
logging.basicConfig()

pd = PickleDict(resource_filename('grounding', 'pickledata'))

objects_and_colors = defaultdict(list)

colorlist = ['blue', 'black', 'brown', 'green', 'grey', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
rgb = {'blue': (0,0,255), 'black': (0,0,0), 'brown': (139, 69, 19), 'green': (0, 255, 0), 'grey': (100,100,100), 'orange': (255, 165,0), 'pink': (255,105,180), 'purple': (160, 32, 240), 'red': (255,0,0), 'white': (255, 255, 255), 'yellow': (255,255,0)}
en = Language.get('en')

def total_distance(array, vec):
    return np.sum(np.sqrt(np.sum((array-vec)**2, axis=1)))

def medianesque(array):
    """
    Given a bunch of vector values (such as colors), return the one closest
    to the median. Samples an arbitrary 100 colors if there are too many to
    analyze efficiently.
    """
    if len(array) > 100: array = random.sample(array, 100)
    array = np.asarray(array)
    distances = [total_distance(array, array[i]) for i in xrange(array.shape[0])]
    return array[np.argmin(distances)]

@pd.lazy(version=2)
def make_color_data():
    # Nodebox
    print "Constructing from NodeBox"
    for color in colorlist:
        data_stream = resource_stream('grounding', 'data/nodebox/' + color + '.txt')
        sets = [x.strip('\n') for x in data_stream.readlines()]
        clist = ','.join(sets)
        words = clist.split(',')            
        for word in words:
            word = word.strip()
            if word == '': continue
            print color, word
            objects_and_colors[en.nl.normalize(word)].append(rgb[color])
        

    # ConceptNet
    print "Constructing from ConceptNet"
    for color in colorlist:
        assertions = Assertion.objects.filter(
            concept2__text=color,
            relation__name='HasProperty',
            language__id='en',
            score__gt=0,
            frequency__value__gt=0,
        )
        for theassertion in assertions:
            object = theassertion.concept1.text
            print color, object
            objects_and_colors[object].append(rgb[color])

    # Color Doctor
    print "Constructing from Color Doctor"
    colorful = ColorAssertion.objects.filter(score__gt=0,)
    for cd in colorful:
        object = cd.concept.text
        ccolor = cd.color
        color = (ccolor.red, ccolor.green, ccolor.blue)
        print color, object
        objects_and_colors[object].append(color)

    # xkcd
    print "Constructing from xkcd"
    xkcd = xkcd_plot.get_plotdata('median_colors').values()
    for entry in xkcd:
        colorname = entry['colorname']
        color = tuple(entry['rgb']*255)
        concepts = en.nl.extract_concepts(colorname, check_conceptnet=True)

        ## add all xkcd names
        #if colorname not in concepts: concepts.append(colorname)
        for concept in concepts:
            objects_and_colors[concept].append(color)

    return objects_and_colors

@pd.lazy(version=2)
def get_colorfulness():
    objects_and_colors = make_color_data()
    print "Finding Uncolorful Concepts"
    colorfulness = defaultdict(list)
    for object in objects_and_colors:
        colorfulness[object].append(1)
    notcolor = NotColorfulAssertion.objects.filter(score__gt=0)
    for lack in notcolor:
        object = lack.concept.text
        print object
        colorfulness[object].append(0)
    return colorfulness

@pd.lazy(version=3)
def make_color_matrix():
    colorfulness = get_colorfulness()
    objects_and_colors = make_color_data()
    objects = divisi2.OrderedSet()
    objects.extend(colorfulness.keys())
    objects.extend(objects_and_colors.keys())
    colors = divisi2.DenseMatrix(row_labels=objects, col_labels=['red','green','blue','colorful'])
    for thing,values in colorfulness.items():
        colorfulness = np.sum(values)/len(values)
        colors.set_entry_named(thing, 'colorful', colorfulness)

    for thing, values in objects_and_colors.items():
        red, green, blue = medianesque(values)

        colors.set_entry_named(thing, 'red', red)
        colors.set_entry_named(thing, 'green', green)
        colors.set_entry_named(thing, 'blue', blue)

    return colors

def x11_matrix():
    colormap = {}
    firstline = True
    for line in resource_stream('grounding', 'data/x11/rgb.txt'):
        if firstline: # skip the header
            firstline = False
            continue
        if line.strip():
            rgb, name = line.strip().split('\t\t')
            r, g, b = rgb.split()
            colormap[name] = np.array([r, g, b])
    colors = divisi2.OrderedSet(colormap.keys())
    matrix = divisi2.DenseMatrix(row_labels=colors,
                                 col_labels=['red', 'green', 'blue',
                                             'colorful'])
    for colorname, rgb in colormap.items():
        matrix[matrix.row_index(colorname), 0:3] = rgb
    matrix[:,3] = 1
    return matrix

def nearest_color(colormat, rgb):
    diffs = np.abs(colormat[:,:3] - rgb)
    distances = np.sum(diffs, axis=-1)
    best = np.argmin(distances)
    return colormat.row_label(best)

def make_colorizer():
    log.info('Loading ConceptNet matrix')
    cnet = divisi2.network.conceptnet_matrix('en')
    log.info('Loading color matrix')
    colors = make_color_matrix()
    log.info('Building colorizer')
    return Colorizer(cnet, colors)

colorizer = make_colorizer()
#x11 = x11_matrix()
