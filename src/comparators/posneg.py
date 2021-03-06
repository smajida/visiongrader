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

from comparator_helpers import compare_images_default, compare_datasets_default
from result import BoolResult

name = "PosNegComparator"

def describe():
    return "Comparator for images containing only a single person or none"

def compare_datasets(toscore, groundtruth):
    raise NotImplementedError()
    result = BoolResult()
    #print groundtruth
    for img in groundtruth:
        len_gt = len(groundtruth[img])
        if img not in toscore:
            if len_gt == 0:
                result.add_true_negative(img)
            else:
                result.add_false_negative(img)
        else:
            len_ts = len(toscore[img])
            if len_gt == 0:
                if len_ts == 0:
                    result.add_true_negative(img)
                else:
                    result.add_false_positive(img)
            else:
                if len_ts == 0:
                    result.add_false_negative(img)
                else:
                    result.add_true_positive(img)
    return result

def set_param(param):
    pass
