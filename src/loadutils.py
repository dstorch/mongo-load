###########################################################
#
# Expand "@" templates in order to support random data
# generation.
#
###########################################################

import numpy as np
import collections

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

expansion_map = {
    "@uniform": expand_uniform,
    "@oneOf": expand_oneof,
    "@normal": expand_normal
}

def expand_prototype_impl(proto, parent_key, parent_proto):
    if isinstance(proto, collections.Iterable):
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
