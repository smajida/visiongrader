#!/usr/bin/python

# Copyright (C) 2010 Michael Mathieu <michael.mathieu@ens.fr>
# 
# This file is part of visiongrader.
# 
# visiongrader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# visiongrader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with visiongrader.  If not, see <http://www.gnu.org/licenses/>.
# 
# Authors :
#  Michael Mathieu <michael.mathieu@ens.fr>

import viewer
import optparse
import os
import os.path
import sys

from result import MultiResult

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
    usage = "usage: %prog -i input -g groundtruth --input_parser inputparser \
--groundtruth_parser groundtruthparser [-c comparator] [OPTIONS] [--roc] [--det]"
    optparser = optparse.OptionParser(add_help_option = True, usage = usage,
                                      prog = "./main.py")
    optparser.add_option("-i", "--input", dest = "input", default = None, type = "str",
                         help = "Input file to score (if not specified, a generator \
must be specified)")
    optparser.add_option("-t", "--groundtruth", dest = "groundtruth", default = None,
                         type = "str", help = "Ground truth file (required)")
    optparser.add_option("--input_parser", dest = "input_parser", default = None,
                         type = "str", help = "Parser to use for the file to score")
    optparser.add_option("--groundtruth_parser", dest = "groundtruth_parser",
                         default = None, type = "str",
                         help = "Parser to use for the ground truth file")
    optparser.add_option("--parser_dir", dest = "parser_dir", default = "parsers",
                         type = "str", help = "Parser directory")
    optparser.add_option("--comparator_dir", dest = "comparator_dir",
                         default = "comparators", type = "str",
                         help = "Comparator directory")
    optparser.add_option("-c", "--comparator", dest = "comparator",
                         default = None, type = "str",
                         help = "Comparator to use (required)")
    optparser.add_option("--roc", dest = "roc", action = "store_true", default = False,
                         help = "Print ROC curve.")
    optparser.add_option("--det", dest = "det", action = "store_true", default = False,
                         help = "Print DET curve.")
    optparser.add_option("--disp", dest = "display", action = "store_true",
                         default = False,
                         help = "Display the images, groundtruths and bounding boxes.")
    optparser.add_option("--confidence_max", dest = "confidence_max", default = None,
                         type = "float",
                         help = "Maximum confidence to display for the curves.")
    optparser.add_option("--confidence_min", dest = "confidence_min", default = None,
                         type = "float",
                         help = "Mminimum confidence to display for the curves.")
    optparser.add_option("--crawl", action = "store_true", dest = "crawl",
                         default = False, help = "Crawls eblearn files.")
    optparser.add_option("--sampling", dest = "sampling", default = None, type = "int",
                         help = "Number of points used to generate the ROC/DET curve..")
    optparser.add_option("--show-no-curve", dest = "show_curve", action = "store_false",
                         help = "Do not display the ROC/DET curve.")
    optparser.add_option("--saving-file", dest = "saving_file", default = None,
                         type = "str", help = "Name of the file to save the curve. \
The curve is not saved if no file is specified.")
    optparser.add_option("--xmin", dest = "xmin", default = None, type = "float",
                         help = "Minimum of the x axis for ROC/DET curve.")
    optparser.add_option("--xmax", dest = "xmax", default = None, type = "float",
                         help = "Maximum of the x axis for ROC/DET curve.")
    optparser.add_option("--ymin", dest = "ymin", default = None, type = "float",
                         help = "Minimum of the y axis for ROC/DET curve.")
    optparser.add_option("--ymax", dest = "ymax", default = None, type = "float",
                         help = "Maximum of the y axis for ROC/DET curve.")
    optparser.add_option("--images_path", dest = "img_path", default = None,
                         type = "str", help = "Path to the images if 'disp' mode.")
    (options, args) = optparser.parse_args()
    
    if options.input == None:
        optparser.print_usage()
        sys.exit(0)
    toscore_filename = options.input

    modes = [("roc", "ROC"), ("det", "DET"), ("display", "display")]
    mode = None
    for (mode_opt, mode_name) in modes:
        if getattr(options, mode_opt) == True:
            if mode != None:
                print "You cannot choose mode than one mode (--roc, --det or --display)."
                sys.exit(0)
            mode = mode_name
    if mode == None:
        mode = "input_file"

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
    toscore_parser = parsers.get_module(options.input_parser) #TODO : check existence
    groundtruth_parser = parsers.get_module(options.groundtruth_parser) #TODO same

    if mode != "display":
        if options.comparator == None:
            print "You must specify a comparator."
            optparser.print_usage()
            sys.exit(0)
        comparator = comparators.get_module(options.comparator)

    groundtruth = groundtruth_parser.parse(groundtruth_filename)
    
    if mode == "input_file":
        toscore = toscore_parser.parse(toscore_filename)
        result = comparator.compare_datasets(toscore, groundtruth)
        print result
    elif mode == "display":
        toscore = toscore_parser.parse(toscore_filename)
        v = viewer.Viewer()
        global i
        i= 0
        def on_click(toscore = toscore, v = v):
            global i
            img_name = toscore.keys()[i]
            filename = groundtruth_parser.get_img_from_name(img_name,
                                                            groundtruth_filename,
                                                            options.img_path)
            img = toscore[img_name]
            print i
            i = (i + 1) % len(toscore)
            v.display(filename, img.get_gprims(), img.get_gprims())
        v.start(on_click, on_click)
    elif mode == "ROC" or mode == "DET":
        import plot
        toscore = toscore_parser.parse_multi(toscore_filename, crawl = options.crawl)
        multi_result = MultiResult()
        print toscore.n_confidences()
        if options.sampling == None:
            n = 200
        else:
            n = int(toscore.n_confidences() / options.sampling)
        for i in xrange(0, n):
            #print i
            confidence = toscore.keys()[toscore.n_confidences() / n * i]
            if options.confidence_min != None:
                if confidence < options.confidence_min:
                    continue
            if options.confidence_max != None:
                if confidence > options.confidence_max:
                    continue
            print i
            dataset = toscore[confidence]
            result = comparator.compare_datasets(dataset, groundtruth)
            multi_result.add_result(result)
        if mode == "ROC":
            if groundtruth_parser.data_type == "images":
                plot.print_ROC(multi_result, len(toscore), options.saving_file,
                               options.show_curve,
                               xmin = xmin, ymin = ymin, xmax = xmax, ymax = ymax)
            elif groundtruth_parser.data_type == "posneg":
                #TODO: bug in plotter
                raise NotImplementedError()
                #plot.print_ROC(multi_result, len(toscore))
                plot.print_ROC_posneg(multi_result)
            else:
                raise NotImplementedError()
        elif mode == "DET":
            if groundtruth_parser.data_type == "images":
                plot.print_DET(multi_result, len(toscore), options.saving_file,
                               options.show_curve,
                               xmin = xmin, ymin = ymin, xmax = xmax, ymax = ymax)
            elif groundtruth_parser.data_type == "posneg":
                #TODO: bug in plotter
                raise NotImplementedError()
                plot.print_DET_posneg(multi_result)
                #plot.print_DET(multi_result, len(toscore))
            else:
                raise NotImplementedError()
        
