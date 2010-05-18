from csc import divisi2
from csc.divisi2.ordered_set import OrderedSet
from color_data import make_color_matrix, lab_to_rgb, make_user_test, make_color_matrix_for_test, medianesque
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
        self.colorfulness = self.smaller_color_matrix[:,3]

    def lab_color_for_concept(self, text):
        if text in self.color_matrix.row_labels:
            return self.color_matrix.row_named(text)

        if text not in self.spreading_activation.row_labels:
            return None

        vector = self.spreading_activation.row_named(text)
        aligned_vector = vector[self.concept_label_map]
        weighted_vector = aligned_vector ** 3
        weighted_vector /= sum(weighted_vector)
        colorfulness = divisi2.dot(aligned_vector.hat(), self.smaller_color_matrix)[3]
        color = divisi2.dot(weighted_vector, self.smaller_color_matrix)[:3]
        return divisi2.DenseVector([color[0], color[1], color[2], colorfulness], OrderedSet(["L", "a", "b", "colorfulness"]))

    def rgb_color_for_concept(self, text):
        l,a,b,c = self.lab_color_for_concept(text)
        r, g, b = lab_to_rgb((l,a,b))
        return divisi2.DenseVector([r, g, b, c], OrderedSet(["red", "green", "blue", "colorfulness"]))


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
    log.info('Loading test info')
    train, test = make_user_test()
    log.info('Building colorizer')
    cmatrix = make_color_matrix_for_test(train)
    colorizer = Colorizer(sa, cmatrix)

    dist_dict = {}
    for concept in test.keys():
        try:
            labout = tuple(colorizer.lab_color_for_concept(concept)[:3])
        except TypeError:
            continue
        labact = medianesque(test[concept])
        dist = euclid(labout,labact)
        dist_dict[concept] = dist
        print concept, labact, labout, str(dist)
    total = sum(dist_dict.values())
    assert False
    return total/len(dist_dict)
        
        
#colorizer = make_colorizer()

print run_leave_n_out()

# vim:tw=0:
