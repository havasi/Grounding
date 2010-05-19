from csc import divisi2
from csc.conceptnet.models import Language, en
from csc.divisi2.ordered_set import OrderedSet
from color_data import make_color_matrix, rgb_to_lab, lab_to_rgb, make_user_test, make_test_data, medianesque, training_and_test_data
import numpy, math
import logging

log = logging.getLogger('colorizer')
log.setLevel(logging.INFO)
logging.basicConfig()

class Colorizer(object):
    def __init__(self, spreading_activation, color_matrix):
        self.spreading_activation = spreading_activation
        self.color_matrix = color_matrix
        self.colorful_concepts = divisi2.OrderedSet(set(color_matrix.row_labels) & set(spreading_activation.row_labels))
        self.color_label_map = [color_matrix.row_labels.index(label) for label in self.colorful_concepts]
        self.concept_label_map = [spreading_activation.row_labels.index(label) for label in self.colorful_concepts]
        self.smaller_color_matrix = self.color_matrix[self.color_label_map]

    def lab_color_for_concept(self, concept):
        if concept in self.color_matrix.row_labels:
            return self.color_matrix.row_named(concept)
        starting_set = en.nl.extract_concepts(concept)
        if not starting_set: return None

        category = divisi2.SparseVector.from_counts(starting_set)
        vector = self.spreading_activation.left_category(category)
        aligned_vector = vector[self.concept_label_map]
        #aligned_vector /= numpy.sum(aligned_vector)
        #color = divisi2.dot(aligned_vector, self.smaller_color_matrix)
        
        sparse_vector = divisi2.SparseVector.from_named_entries([(value, key) for (key, value) in aligned_vector.top_items(10)])
        sparse_vector /= sparse_vector.vec_op(numpy.sum)
        color = divisi2.aligned_matrix_multiply(sparse_vector, self.smaller_color_matrix)[:3]

        #print concept, ':'
        #for key, value in aligned_vector.top_items(9):    
        #    print '\t', key, value, lab_to_rgb(self.color_matrix.row_named(key))
        #best_colors = [self.color_matrix.row_named(x[0]) for x in aligned_vector.top_items(9)]
        #color = medianesque(best_colors)
        #print '\t', lab_to_rgb(color)

        return divisi2.DenseVector(color, OrderedSet(["L", "a", "b"]))

    def rgb_color_for_concept(self, text):
        l,a,b = self.lab_color_for_concept(text)
        r, g, b = lab_to_rgb((l,a,b))
        return divisi2.DenseVector([r, g, b], OrderedSet(["red", "green", "blue"]))

def make_colorizer():
    from csc.divisi2 import examples
    log.info('Loading ConceptNet matrix')
    sa = examples.spreading_activation()
    log.info('Loading color matrix')
    colors = make_color_matrix()
    log.info('Building colorizer')
    return Colorizer(sa, colors)

def euclid(t1, t2):
    sumofsquares = 0
    for x in range(len(t1)):
        sumofsquares += (float(t1[x]) - float(t2[x]))**2
    return math.sqrt(sumofsquares)
    
def run_leave_n_out():
    from csc.divisi2 import examples
    import colors
    log.info('Loading ConceptNet matrix')
    sa = examples.spreading_activation()
    log.info('Loading test input')
    train_input, test_input = training_and_test_data()
    log.info('Loading test data')
    test = make_test_data()
    log.info('Building colorizer')
    cmatrix = make_color_matrix()
    colorizer = Colorizer(sa, cmatrix)

    dist_dict = {}
    baseline_dict = {}
    distances = {
        'baseline': [],
        'weighted': [],
        'nodebox_prism': [],
        'inter_annotator': [],
    }

    test_concepts = set(test.keys()) & set(sa.row_labels)
    for colorname in test_concepts:
        try:
            labout = tuple(colorizer.lab_color_for_concept(colorname)[:3])
        except TypeError:
            continue
        labact = test[colorname]
        dist = euclid(labout,labact)
        
        distances['weighted'].append(dist)

        baseline = euclid([50, 0, 0], labact)
        distances['baseline'].append(baseline)
        
        try:
            prismdata = [rgb_to_lab([color.__r, color.__g, color.__b]) for color in colors.prism(colorname)]
            prism_avg = numpy.mean(numpy.array(prismdata), axis=0)
            prism_dist = euclid(prism_avg, labact)
            distances['nodebox_prism'].append(prism_dist)
        except ZeroDivisionError:
            pass

        inter_annotator = euclid(rgb_to_lab(test_input[colorname][0]), 
                                 labact)
        if inter_annotator == 0:
            inter_annotator = euclid(rgb_to_lab(test_input[colorname][1]), 
                                     labact)
        distances['inter_annotator'].append(inter_annotator)
        
        rgbact = lab_to_rgb(labact)
        rgbout = lab_to_rgb(labout)

        print colorname, rgbact, rgbout, str(dist)
    
    totals = {}
    for key, values in distances.items():
        totals[key] = sum(values)/len(values)
    print totals
    return totals

#colorizer = make_colorizer()
if __name__ == '__main__':
    print run_leave_n_out()

# vim:tw=0:
