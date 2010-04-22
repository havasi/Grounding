from csc import divisi2
import numpy

class Colorizer(object):
    def __init__(self, concept_matrix, color_matrix):
        self.concept_matrix = concept_matrix
        self.color_matrix = color_matrix
        self.overlap_labels = divisi2.OrderedSet(set(color_matrix.row_labels) & set(concept_matrix.row_labels))
        self.color_label_map = [color_matrix.row_labels.index(label) for label in self.overlap_labels]
        self.concept_label_map = [concept_matrix.row_labels.index(label) for label in self.overlap_labels]

        self.U, self.S, self.V = concept_matrix.normalize_all().svd(k=100)
        self.U_slice = self.U[self.concept_label_map, :]
        self.colors_slice = color_matrix[self.color_label_map, :]

    def color_for_concept(self, text):
        if text not in self.U.row_labels: return None
        vector = self.U.row_named(text)
        
        non_color_weight = numpy.maximum(0, divisi2.dot(self.U_slice * self.S * self.S, vector))**3
        color_weight = non_color_weight * self.colors_slice[:, 3]
        
        total_nc_weight = numpy.sum(non_color_weight)
        total_weight = numpy.sum(color_weight)

        avg_color = divisi2.dot(color_weight, self.colors_slice) / total_weight
        avg_nc = divisi2.dot(non_color_weight, self.colors_slice) / total_nc_weight

        result = numpy.zeros((4,))
        result[0:3] = avg_color[0:3]
        result[3] = avg_nc[3]
        return result

# vim:tw=0:
