#!/usr/bin/python

import optparse
import os
import os.path
import sys
import plot

from result import ROCResult

class ModuleHandler(object):
    def __init__(self, module_dir, module_name):
        self.modules = {}
        self.module_name = module_name
        modules_names = os.listdir(os.path.join(module_dir, module_name))
        if module_dir not in sys.path:
            sys.path.append(os.path.abspath(module_dir))
            remove_from_path = True
        else:
            remove_from_path = False
        __import__(module_name)
        for name in modules_names:
            if self.is_a_module_name(name):
                name = "%s.%s"%(module_name, name[:-3])
                __import__(name)
                self.modules[name] = sys.modules[name]
        if remove_from_path:
            sys.path.remove(os.path.abspath(module_dir))

    def is_a_module_name(self, name):
        return name[-3:] == ".py"

    def get_modules_names(self):
        return self.modules.keys()

    def get_module(self, name):
        return self.modules["%s.%s"%(self.module_name, name)]

if __name__=="__main__":
    usage = "usage: %prog -g groundtruth --input_parser inputparser --groundtruth_parser \
    groundtruthparser -c comparator [OPTIONS] [-i input] [-g generator] [--roc] [--det]"
    optparser = optparse.OptionParser(add_help_option = True, usage = usage, prog = "./main.py")
    optparser.add_option("-i", "--input", dest = "input", default = None, type = "str",
                         help = "Input file to score (if not specified, a generator must be specified)")
    optparser.add_option("-t", "--groundtruth", dest = "groundtruth", default = None, type = "str",
                         help = "Ground truth file (required)")
    optparser.add_option("--input_parser", dest = "input_parser", default = None, type = "str",
                         help = "Parser to use for the file to score")
    optparser.add_option("--groundtruth_parser", dest = "groundtruth_parser", default = None, type = "str",
                         help = "Parser to use for the ground truth file")
    optparser.add_option("--parser_dir", dest = "parser_dir", default = "parsers", type = "str",
                         help = "Parser directory")
    optparser.add_option("--comparator_dir", dest = "comparator_dir", default = "comparators",
                         type = "str", help = "Comparator directory")
    optparser.add_option("-c", "--comparator", dest = "comparator", default = None, type = "str",
                         help = "Comparator to use (required)")
    optparser.add_option("--generator_dir", dest = "generator_dir", default = "generators", type = "str",
                         help = "Generator directory")
    optparser.add_option("-g", "--generator", dest = "generator", default = None, type = "str",
                         help = "Generator to use (if not specified, an input file must be specified")
    optparser.add_option("--images_dir", dest = "images_path", default = None, type = "str",
                         help = "Path to the images to generate from")
    optparser.add_option("--generated_dir", dest = "generated_dir", default = "generated", type = "str",
                         help = "Directory to pick and put the generated files in case of generate mode")
    optparser.add_option("--roc", dest = "roc", action = "store_true", default = False,
                         help = "Print ROC curve. Can only work with a generator.")
    optparser.add_option("--det", dest = "det", action = "store_true", default = False,
                         help = "Print DET curve. Can only work with a generator.")
    (options, args) = optparser.parse_args()

    if options.input != None:
        toscore_filename = options.input
        mode = "input_file"
        if options.roc or options.det:
            print "You must use a generator to use --roc or --det option."
            sys.exit(0)
    elif options.generator != None:
        generator_dir = options.generator_dir
        generators = ModuleHandler(".", generator_dir)
        generator = generators.get_module(options.generator)
        if options.roc and options.det:
            print "You cannot choose both --roc and --det."
            sys.exit(0)
        if options.roc:
            mode = "ROC"
        elif options.det:
            mode = "DET"
        else:
            print "Choose either --roc od --det."
            sys.exit(0)
    else:
        optparser.print_usage()
        sys.exit(0)
    if options.groundtruth == None:
        optparser.print_usage()
        sys.exit(0)
    groundtruth_filename = options.groundtruth

    parser_dir = options.parser_dir
    comparator_dir = options.comparator_dir
    parsers = ModuleHandler(".", parser_dir)
    comparators = ModuleHandler(".", comparator_dir)

    if options.input_parser == None or options.groundtruth_parser == None:
        optparser.print_usage()
        sys.exit(0)
    #print parsers.modules
    #print parsers.modules[options.input_parser].describe()
    toscore_parser = parsers.get_module(options.input_parser) #TODO : check existence
    groundtruth_parser = parsers.get_module(options.groundtruth_parser) #TODO same

    if options.comparator == None:
        optparser.print_usage()
        sys.exit(0)
    comparator = comparators.get_module(options.comparator)

    groundtruth_file = open(groundtruth_filename, "r")
    groundtruth = groundtruth_parser.parse(groundtruth_file)
    groundtruth_file.close()
    
    if mode == "input_file":
        toscore_file = open(toscore_filename, "r")
        toscore = toscore_parser.parse(toscore_file)
        toscore_file.close()
        result = comparator.compare_datasets(toscore, groundtruth)
        print result
    elif mode == "ROC" or mode == "DET":
        thresholds = generator.thresholds
        roc_result = ROCResult()
        for threshold in thresholds:
            #TODO create generated
            dest = os.path.join(options.generated_dir, "bbox%f.txt"%(threshold,))
            if not os.path.exists(dest):
                if options.images_path == None:
                    print "No image directory specified"
                    sys.exit(0)
                generator.generate(options.images_path, threshold, dest)
            toscore_file = open(dest, "r")
            print dir(toscore_parser)
            toscore = toscore_parser.parse(toscore_file)
            toscore_file.close()
            result = comparator.compare_datasets(toscore, groundtruth)
            print "Threshold = %f"%(threshold)
            print result
            roc_result.add_result(threshold, result)
        print roc_result
        if mode == "ROC":
            plot.print_ROC(roc_result)
        elif mode == "DET":
            plot.print_DET(roc_result)
