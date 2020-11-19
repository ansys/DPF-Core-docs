##########################################################################
#                                                                        #
#          Copyright (C) 2020 ANSYS Inc.  All Rights Reserved            #
#                                                                        #
# This file contains proprietary software licensed from ANSYS Inc.       #
# This header must remain in any source code despite modifications or    #
# enhancements by any party.                                             #
#                                                                        #
##########################################################################
# Version: 1.0                                                           #
# Author(s): C.Bellot/R.Lagha                                            #
# contact(s): ramdane.lagha@ansys.com                                    #
##########################################################################
"""Common dpf methods """
from enum import Enum

import numpy as np
import re

from ansys.grpc.dpf import base_pb2 as base_pb2

def camel_to_snake_case(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def remove_spaces(name):
    out = name.lower()
    out = out.replace(" ", "_") 
    out = out.replace("-", "_") 
    return out

def snake_to_camel_case(name):
    return ''.join(word.title() for word in name.split('_'))

class smart_dict_camel(dict):
    def __missing__(self, key):
        return camel_to_snake_case(key)
    
class smart_dict_unit_system(dict):
    def __missing__(self, key):
        return 'unknown'

names = [m.lower() for m in base_pb2.Type.keys()]
names.append("fields_container")
types = Enum('types', names)

names = [m.lower() for m in base_pb2.Nature.keys()]
natures = Enum('natures', names)


class locations:
    """Contains python field types"""
    none = "none"

    # data is one per element
    elemental = "Elemental"

    # one per node per element
    elemental_nodal = "ElementalNodal"

    # one per node
    nodal = "Nodal"

    # one per time step
    time_freq = "TimeFreq_sets"
    
    #applies everywhere
    overall="overall"
            


def field_from_array(arr):
    """Creates DPF vector or scalar field from a numpy array or a
    Python list.

    Parameters
    ----------
    arr : np.ndarray or List
        Numpy array or Python List containing either 1 or 3 dimensions.

    Returns
    -------
    field : ansys.dpf.Field
        Field constructed from numpy array.
    """
    from ansys.dpf import Field, natures
    arr = np.asarray(arr)

    if not np.issubdtype(arr.dtype, np.number):
        raise TypeError('Array must be a numeric type')

    shp_err = ValueError('Array must be either contain 1 dimension or '
                         '2 dimensions with three components.')
    if arr.ndim == 1:
        nature = natures.scalar
    elif arr.ndim == 2:
        if arr.shape[1] == 1:
            arr = arr.ravel()
            nature = natures.scalar
        elif arr.shape[1] == 3:
            nature = natures.vector
        elif arr.shape[1] == 6:
            nature = natures.symmatrix
        else:
            raise shp_err
    else:
        raise shp_err

    # TODO: speedup, very inefficient
    nentities = arr.shape[0]
    ids=[]
    field = Field(nentities=nentities, nature=nature)
    field.data = arr
        
    for i in range(nentities):
        ids.append(i+1)
    
    field.scoping.ids =ids

    return field

