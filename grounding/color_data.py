from pkg_resources import resource_filename, resource_stream
from collections import defaultdict
from csc.conceptnet.models import RightFeature, Assertion, Language
from grounding.models import ColorAssertion, NotColorfulAssertion
from csc.util.persist import PickleDict
from csc import divisi2
from colormath.color_objects import LuvColor, LabColor, RGBColor
import numpy as np
import logging
import random
import math

def rgb_to_luv(rgb):
    rgbcolor = RGBColor(*rgb)
    luvcolor = rgbcolor.convert_to('xyz').convert_to('luv')
    return (luvcolor.luv_l, luvcolor.luv_u, luvcolor.luv_v)

def rgb_to_wheel(rgb):
    rgbcolor = RGBColor(*rgb)
    hsvcolor = rgbcolor.convert_to('hsv')
    angle = hsvcolor.hsv_h*2*math.pi/360
    return (math.sin(angle) * hsvcolor.hsv_s, math.cos(angle) * hsvcolor.hsv_s)

def rgb_to_lab(rgb):
    rgbcolor = RGBColor(*rgb)
    labcolor = rgbcolor.convert_to('lab')
    return (labcolor.lab_l, labcolor.lab_a, labcolor.lab_b)

def lab_to_rgb(lab):
    labcolor = LabColor(*lab)
    rgbcolor = labcolor.convert_to('rgb')
    return (rgbcolor.rgb_r, rgbcolor.rgb_g, rgbcolor.rgb_b)

def luv_to_rgb(luv):
    luvcolor = LuvColor(*luv)
    rgbcolor = luvcolor.convert_to('rgb')
    return (rgbcolor.rgb_r, rgbcolor.rgb_g, rgbcolor.rgb_b)

log = logging.getLogger('colorizer')
log.setLevel(logging.INFO)
logging.basicConfig()

pd = PickleDict(resource_filename('grounding', 'pickledata'), gzip=False)

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

def component_median(array):
    return np.median(array, axis=0)

@pd.lazy(version=1)
def xkcd_data():
    xkcd = defaultdict(list)

    with open('grouped_color_data.txt') as inputlines:
        for line in inputlines:
            try:
                colorname, userid, r, g, b, monitor, colorblind, male = line.strip().split('|')
            except ValueError:
                continue
            rgblist = [float(r), float(g), float(b)]
            xkcd[colorname].append(rgblist)
            print colorname.decode('utf-8').encode('ascii', 'replace')
    return xkcd

@pd.lazy(version=1)
def training_and_test_data():
    print "Constructing test/train from xkcd"
    train = defaultdict(list)
    test = defaultdict(list)
    combined = defaultdict(list)

    with open('grouped_color_data.txt') as inputlines:
        for line in inputlines:
            try:
                colorname, userid, r, g, b, monitor, colorblind, male = line.strip().split('|')
            except ValueError:
                continue
            rgblist = [float(r), float(g), float(b)]
            combined[colorname].append(rgblist)
            print colorname.decode('utf-8').encode('ascii', 'replace')
    
    #for colorname in combined.keys():
    #    if len(combined[colorname]) < 3:
    #        del combined[colorname]
    
    from csc.divisi2.examples import spreading_activation
    spread = spreading_activation()
    import random
    possible_concepts = set(spread.row_labels) & set(combined)
    test_concepts = random.sample(possible_concepts, 200)
    out = open('test_concepts.txt', 'w')
    for concept in test_concepts:
        print "Test concept:", concept
        print >> out, concept
    out.close()

    training = True
    for colorname in combined:
        concepts = en.nl.extract_concepts(colorname, check_conceptnet=True)
        censored = False
        for concept in concepts:
            if concept in test_concepts:
                censored = True
        if censored: target = test
        else: target = train
        target[colorname] = combined[colorname]
    return train, test

@pd.lazy(version=2)
def make_lab_color_data():
    """
    Returns a dictionary mapping color names to lists of Lab color values.
    """
    objects_and_colors = defaultdict(list)
    xkcd = xkcd_data()  # formerly used training data with held-out tests

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
            for i in xrange(100):
                objects_and_colors[en.nl.normalize(word)].append(rgb_to_lab(rgb[color]))

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
            for i in xrange(100):
                objects_and_colors[object].append(rgb_to_lab(rgb[color]))

    # xkcd
    print "Constructing from xkcd"
    for text in xkcd:
        concepts = en.nl.extract_concepts(text, check_conceptnet=True)
        for concept in concepts:
            objects_and_colors[concept].extend([rgb_to_lab(x) for x in xkcd[text]])
            print concept

    return objects_and_colors

@pd.lazy(version=2)
def make_user_test():
    import random
    dict = make_lab_color_data()
    keys = dict.keys()
    training_dict = {}
    test_dict = {}
    for key in keys:
        if random.random() < 0.5:
            training_dict[key] = dict[key]
        else:
            test_dict[key] = dict[key]
    return (training_dict, test_dict)
    
9
@pd.lazy(version=2)
def make_color_data():
    from grounding import xkcd_plot
    objects_and_colors = defaultdict(list)

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

@pd.lazy(version=3)
def get_colorfulness():
    objects_and_colors = make_lab_color_data()
    print "Finding Uncolorful Concepts"
    colorfulness = {}
    for object in objects_and_colors:
        yes = 0
        no = 100
        yes += len(objects_and_colors[object])
        no += NotColorfulAssertion.objects.filter(score__gt=0, concept__text=object).count()
        colorfulness[object] = float(yes) / (yes+no)
    return colorfulness

@pd.lazy(version=4)
def make_color_matrix():
    colorfulness = get_colorfulness()
    objects_and_colors = make_lab_color_data()
    objects = divisi2.OrderedSet()
    #objects.extend(colorfulness.keys())
    objects.extend(objects_and_colors.keys())
    colors = divisi2.DenseMatrix(row_labels=objects, col_labels=['L','a','b','colorful'])

    for thing, values in objects_and_colors.items():
        L, a, b = np.mean(np.array(values), axis=0)

        colors.set_entry_named(thing, 'L', L)
        colors.set_entry_named(thing, 'a', a)
        colors.set_entry_named(thing, 'b', b)
        colors.set_entry_named(thing, 'colorful', colorfulness[thing])

    return colors

@pd.lazy(version=1)
def make_test_data():
    train, test = training_and_test_data()
    testdata = {}
    for colorname in test:
        if len(test[colorname]) >= 3:
            testdata[colorname] = medianesque([rgb_to_lab(c) for c in test[colorname]])
    return testdata

def nearest_color(colormat, rgb):
    lab = rgb_to_lab(rgb)
    diffs = np.abs(colormat[:,:3] - lab)
    distances = np.sum(diffs, axis=-1)
    best = np.argmin(distances)
    return colormat.row_label(best)

