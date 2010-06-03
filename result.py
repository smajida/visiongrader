class ImageResult(object):
    def __init__(self):
        self.true_positives = []
        self.false_positives = []
        self.false_negatives = []

    def add_true_positive(self, box1, box2):
        self.true_positives.append((box1, box2))
        #print "match", box1, box2

    def add_false_positive(self, box):
        self.false_positives.append(box)
        #print "false positive", box

    def add_false_negative(self, box):
        self.false_negatives.append(box)
        #print "missed", box

    def n_true_positives(self):
        return len(self.true_positives)

    def n_false_positives(self):
        return len(self.false_positives)

    def n_false_negatives(self):
        return len(self.false_negatives)


class DataSetResult(object):
    def __init__(self):
        self.images_results = []
        self._n_true_positives = 0
        self._n_false_positives = 0
        self._n_false_negatives = 0

    def add_image_result(self, result):
        self.images_results.append(result)
        self._n_true_positives += result.n_true_positives()
        self._n_false_positives += result.n_false_positives()
        self._n_false_negatives += result.n_false_negatives()

    def n_true_positives(self):
        return self._n_true_positives

    def n_false_positives(self):
        return self._n_false_positives

    def n_false_negatives(self):
        return self._n_false_negatives

    def __str__(self):
        return "DataSetResult : %d true positives, %d false positive, \
        %d false negatives"%(self.n_true_positives(), self.n_false_positives(),
                             self.n_false_negatives())
class MultiResult(object):
    def __init__(self):
        self.datasets = []

    def add_result(self, result):
        self.datasets.append(result)

    def __str__(self):
        ret = "MultiResult : "
        for th in self.datasets:
            ret += "%s "%(self.datasets[th],)
        return ret[:-1]

    def __getitem__(self, i):
        return self.datasets[i]

class BoolResult(object):
    def __init__(self):
        self.images = {}

    def add_true_positive(self, filename):
        #print "tp"
        if filename in self.images:
            print "Warning : BoolResult : %s already exists."%(filename,)
        self.images[filename] = "TP"

    def add_false_positive(self, filename):
        #print "fp"
        if filename in self.images:
            print "Warning : BoolResult : %s already exists."%(filename,)
        self.images[filename] = "FP"

    def add_true_negative(self, filename):
        #print "tn"
        if filename in self.images:
            print "Warning : BoolResult : %s already exists."%(filename,)
        self.images[filename] = "TN"

    def add_false_negative(self, filename):
        #print "fn"
        if filename in self.images:
            print "Warning : BoolResult : %s already exists."%(filename,)
        self.images[filename] = "FN"

    def n_true_positives(self):
        return self.images.values().count("TP")

    def n_false_positives(self):
        return self.images.values().count("FP")

    def n_true_negatives(self):
        return self.images.values().count("TN")

    def n_false_negatives(self):
        return self.images.values().count("FN")
