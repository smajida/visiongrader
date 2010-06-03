from dataset import DataSet, DataSetMulti
from objects import BoundingBox

name = "eblearnParser"

data_type = "images"

def desctibe():
    return "Parser for eblearn result files"

def recognize(file):
    return False

def parse(filen):
    file = open(filen, "r")
    ret = DataSet()
    for line in file:
        line = line.strip().rstrip()
        splited = line.split()
        filename = splited[0]
        filename = filename[filename.rfind("/")+1:]
        filename = filename[:filename.rfind(".")]
        class_id = int(splited[1])
        (confidence, x, y, x2, y2) = tuple([float(a) for a in splited[2:]])
        if confidence > 1.5: #TODO
            ret.add_obj(filename, BoundingBox(x, y, x2, y2))
    file.close()
    return ret

def parse_multi(filen):
    file = open(filen, "r")
    ret = DataSetMulti()
    for line in file:
        line = line.strip().rstrip()
        splited = line.split()
        filename = splited[0]
        filename = filename[filename.rfind("/")+1:]
        filename = filename[:filename.rfind(".")]
        class_id = int(splited[1])
        (confidence, x, y, x2, y2) = tuple([float(a) for a in splited[2:]])
        ret.add_obj(confidence, filename, BoundingBox(x, y, x2, y2))
    file.close()
    return ret
