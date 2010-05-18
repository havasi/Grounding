from csc import divisi2
from csc.conceptnet.models import Language, en
from csc.divisi2.ordered_set import OrderedSet
from color_data import make_color_matrix, lab_to_rgb, make_user_test, make_test_data, medianesque
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
        assert concept in self.spreading_activation.row_labels

        vector = self.spreading_activation.row_named(concept)
        aligned_vector = vector[self.concept_label_map]
        #aligned_vector /= numpy.sum(aligned_vector)
        #color = divisi2.dot(aligned_vector, self.smaller_color_matrix)
        print concept, ':'
        for key, value in aligned_vector.top_items(9):
            print '\t', key, value, lab_to_rgb(self.color_matrix.row_named(key))
        best_colors = [self.color_matrix.row_named(x[0]) for x in aligned_vector.top_items(9)]
        color = medianesque(best_colors)
        print '\t', lab_to_rgb(color)

        return divisi2.DenseVector(color, OrderedSet(["L", "a", "b"]))

    def lab_color_for_text(self, text):
        #if text in self.color_matrix.row_labels:
        #    return self.color_matrix.row_named(text)

        concepts = en.nl.extract_concepts(text, check_conceptnet=True)
        if not concepts: return None
        category = divisi2.SparseVector.from_counts(concepts)
        vector = self.spreading_activation.left_category(category)
        aligned_vector = vector[self.concept_label_map]
        #aligned_vector /= numpy.sum(aligned_vector)
        #color = divisi2.dot(aligned_vector, self.smaller_color_matrix)
        print concepts
        for key, value in aligned_vector.top_items(9):
            print '\t', key, lab_to_rgb(self.color_matrix.row_named(key))
        best_colors = [self.color_matrix.row_named(x[0]) for x in aligned_vector.top_items(9)]
        color = medianesque(best_colors)
        print '\t', lab_to_rgb(color)

        return divisi2.DenseVector(color, OrderedSet(["L", "a", "b"]))

    def rgb_color_for_text(self, text):
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
    log.info('Loading ConceptNet matrix')
    sa = examples.spreading_activation()
    log.info('Loading test data')
    test = make_test_data()
    log.info('Building colorizer')
    cmatrix = make_color_matrix()
    colorizer = Colorizer(sa, cmatrix)

    dist_dict = {}
    test_concepts = set(test.keys()) & set(sa.row_labels)
    for colorname in test_concepts:
        try:
            labout = tuple(colorizer.lab_color_for_concept(colorname)[:3])
        except TypeError:
            continue
        labact = test[colorname]
        dist = euclid(labout,labact)
        dist_dict[colorname] = dist
        rgbact = lab_to_rgb(labact)
        rgbout = lab_to_rgb(labout)
        print colorname, rgbact, rgbout, str(dist)
    total = sum(dist_dict.values())
    print total, len(dist_dict)
    return total/len(dist_dict)

#colorizer = make_colorizer()
if __name__ == '__main__':
    print run_leave_n_out()

# vim:tw=0:
