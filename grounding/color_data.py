from pkg_resources import resource_filename, resource_stream
from collections import defaultdict
from csc.conceptnet4.models import RightFeature, Assertion, Language
from grounding.models import ColorAssertion, NotColorfulAssertion
from csc.util.persist import PickleDict
from csc import divisi2
from grounding.colorizer import Colorizer
import numpy
import logging

log = logging.getLogger('colorizer')
log.setLevel(logging.INFO)
logging.basicConfig()

pd = PickleDict(resource_filename('grounding', 'pickledata'))

objects_and_colors = defaultdict(list)

colorlist = ['blue', 'black', 'brown', 'green', 'grey', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
rgb = {'blue': (0,0,255), 'black': (0,0,0), 'brown': (139, 69, 19), 'green': (0, 255, 0), 'grey': (100,100,100), 'orange': (255, 165,0), 'pink': (255,105,180), 'purple': (160, 32, 240), 'red': (255,0,0), 'white': (255, 255, 255), 'yellow': (255,255,0)}
en = Language.get('en')

@pd.lazy(version=1)
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
    return objects_and_colors

@pd.lazy(version=1)
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

@pd.lazy(version=1)
def make_color_matrix():
    colorfulness = get_colorfulness()
    objects_and_colors = make_color_data()
    objects = divisi2.OrderedSet()
    objects.extend(colorfulness.keys())
    objects.extend(objects_and_colors.keys())
    colors = divisi2.DenseMatrix(row_labels=objects, col_labels=['red','green','blue','colorful'])
    for thing,values in colorfulness.items():
        colorfulness = numpy.sum(values)/len(values)
        colors.set_entry_named(thing, 'colorful', colorfulness)

    for thing, values in objects_and_colors.items():
        red = numpy.sum([x[0] for x in values])/len(values)
        green = numpy.sum([x[1] for x in values])/len(values)
        blue = numpy.sum([x[2] for x in values])/len(values)

        colors.set_entry_named(thing, 'red', red)
        colors.set_entry_named(thing, 'green', green)
        colors.set_entry_named(thing, 'blue', blue)

    return colors

def make_colorizer():
    log.info('Loading ConceptNet matrix')
    cnet = divisi2.network.conceptnet_matrix('en')
    log.info('Loading color matrix')
    colors = make_color_matrix()
    log.info('Building colorizer')
    return Colorizer(cnet, colors)

colorizer = make_colorizer()
