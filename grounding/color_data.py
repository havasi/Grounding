from pkg_resources import resource_filename, resource_stream
from collections import defaultdict
from csc.conceptnet4.models import RightFeature, Assertion, Language
from grounding.models import ColorAssertion, NotColorfulAssertion
from csc.divisi.util import get_picklecached_thing

objects_and_colors = defaultdict(list)

colorlist = ['blue', 'black', 'brown', 'green', 'grey', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
rgb = {'blue': (0,0,255), 'black': (0,0,0), 'brown': (139, 69, 19), 'green': (0, 255, 0), 'grey': (100,100,100), 'orange': (255, 165,0), 'pink': (255,105,180), 'purple': (160, 32, 240), 'red': (255,0,0), 'white': (255, 255, 255), 'yellow': (255,255,0)}
en = Language.get('en')

def make_color_data():
    # Nodebox
    print "Constructing from NodeBox"
    for color in colorlist:
        data_stream = resource_stream('grounding', 'nodebox_data/' + color + '.txt')
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

def get_not_colorful_concepts(objects_and_colors):
    print "Finding Uncolorful Concepts"
    color_or_country = defaultdict(list)
    for object in objects_and_colors:
        color_or_country[object].append(1)
    notcolor = NotColorfulAssertion.objects.filter(score__gt=0)
    for lack in notcolor:
        object = lack.concept.text
        print object
        color_or_country[object].append(0)
    return color_or_country
        
objects_and_colors = get_picklecached_thing('objects_and_colors.pickle', make_color_data)
color_or_country = get_picklecached_thing('colorfulness.pickle', lambda: get_not_colorful_concepts(objects_and_colors))
