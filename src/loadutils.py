###########################################################
#
# Expand "@" templates in order to support random data
# generation.
#
###########################################################

from copy import deepcopy
import numpy as np
import collections
from pymongo import ASCENDING, DESCENDING

def expand_uniform(proto, key, parent_proto):
    # Error checking
    if not isinstance(proto, dict):
        raise ValueError("Fatal: @uniform requires a subobject.")
    if len(proto) != 3:
        raise ValueError("Fatal: @uniform requires exactly three fields.")
    if "start" not in proto:
        raise ValueError("Fatal: @uniform requires a 'start' field.")
    if "end" not in proto:
        raise ValueError("Fatal: @uniform requires an 'end' field.")
    if "type" not in proto:
        raise ValueError("Fatal: @uniform requires a 'type' field.")

    if proto["type"] != "int" and proto["type"] != "float":
        raise ValueError("Fatal: @uniform 'type' arg must be either 'int' or 'float'.")

    if proto["type"] == "int":
        start = int(proto["start"])
        end = int(proto["end"])
        parent_proto[key] = np.random.randint(start, end)
    else:
        start = float(proto["start"])
        end = float(proto["end"])
        parent_proto[key] = np.random.random() * (end - start) + start

def expand_oneof(proto, key, parent_proto):
    if not isinstance(proto, list):
        raise ValueError("Fatal: @oneOf requires an array.")
    index = np.random.randint(0, len(proto))
    parent_proto[key] = proto[index]

def expand_normal(proto, key, parent_proto):
    # Error checking
    if not isinstance(proto, dict):
        raise ValueError("Fatal: @normal requires a subobject.")
    if len(proto) != 3:
        raise ValueError("Fatal: @normal requires exactly three fields.")
    if "mu" not in proto:
        raise ValueError("Fatal: @normal requires a 'mu' field.")
    if "sigma" not in proto:
        raise ValueError("Fatal: @normal requires an 'sigma' field.")
    if "type" not in proto:
        raise ValueError("Fatal: @normal requires a 'type' field.")

    if proto["type"] != "int" and proto["type"] != "float":
        raise ValueError("Fatal: @normal 'type' arg must be either 'int' or 'float'.")

    mu = float(proto["mu"])
    sigma = float(proto["sigma"])
    sample = np.random.randn() * sigma + mu

    if proto["type"] == "int":
        parent_proto[key] = int(sample)
    else:
        parent_proto[key] = sample

def expand_array(proto, key, parent_proto):
    # Error checking
    if not isinstance(proto, dict):
        raise ValueError("Fatal: @array requires a subobject.")
    if len(proto) != 2:
        raise ValueError("Fatal: @array requires exactly two fields.")
    if "maxSize" not in proto:
        raise ValueError("Fatal: @array requires a 'maxSize' field.")
    if "docs" not in proto:
        raise ValueError("Fatal: @array requires an 'docs' field.")
    if not isinstance(proto["docs"], dict):
        raise ValueError("Fatal: @array 'docs' field must be a subobject.")

    maxSize = int(proto["maxSize"])
    size = np.random.randint(0, maxSize+1)
    docs = proto["docs"]

    # Generate the subdocuments.
    parent_proto[key] = []
    for i in range(0, size):
        to_expand = deepcopy(docs)
        expand_prototype(to_expand)
        parent_proto[key].append(to_expand)


expansion_map = {
    "@uniform": expand_uniform,
    "@oneOf": expand_oneof,
    "@normal": expand_normal,
    "@array": expand_array
}

def expand_prototype_impl(proto, parent_key, parent_proto):
    if isinstance(proto, dict):
        for key in proto:
            if key[0] == "@":
                if key not in expansion_map:
                    raise ValueError("Fatal: unknown prototype expansion: '" + key + "'.")
                expansion_map[key](proto[key], parent_key, parent_proto)
            else:
                expand_prototype_impl(proto[key], key, proto)

def expand_prototype(proto):
    expand_prototype_impl(proto, None, None)

def discrete_sample(probs, numsamples):
    bins = np.add.accumulate(probs)
    return np.digitize(np.random.random_sample(numsamples), bins)

def convert_keypattern(kp):
    keydir_pairs = []
    for field in kp:
        direction = int(kp[field])
        if direction != 1 and direction != -1:
            raise ValueError("Fatal: index direction must be either "
                             + "1 (ascending) or -1 (descending)");
        pair = (field, (ASCENDING if direction == 1 else DESCENDING))
        keydir_pairs.append(pair)
    return keydir_pairs
