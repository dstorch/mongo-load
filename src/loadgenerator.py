###########################################################
#
# Creates a test workload and writes it to a file.
#
###########################################################

from copy import deepcopy
from src import loadutils
from os import path, remove
import json
import sys

class WorkloadGenerator:

    generated = 0
    workload_data = []

    def __init__(self, idnum, ops, params):
        if len(ops) == 0:
            print "Warning: empty 'ops' array. No load will be applied."

        # Validate 'docs'.
        for el in ops:
            if not isinstance(el, dict):
                raise ValueError("Fatal: all elements of 'ops' must be subdocuments.")
            if len(el) != 2:
                raise ValueError("Fatal: elements of 'ops' must contain exactly two fields.")
            if "proto" not in el:
                raise ValueError("Fatal: missing 'proto' field found in 'ops' array.")
            if "prob" not in el:
                raise ValueError("Fatal: missing 'prob' field found in 'ops' array.")

        self.idnum = idnum
        self.ops = ops

        # Generate the path name at which we will store this workload.
        workload_path = path.join(params.workload_dir, "workload" + str(idnum))

        if path.exists(workload_path):
            sys.stderr.write("Warning: file '" + workload_path + "' exists."
                             + " It is being removed.\n")
            remove(workload_path)

        self.workload_file = open(workload_path, "w")

        # Do the same number of ops regardless of the concurrency factor.
        self.workload_size = params.workload_size / params.concurrency

        # Sample from the discrete probability distribution defined by the "prob"
        # values in the ops array.
        probs = [float(d["prob"]) for d in ops]
        self.ops_sample = loadutils.discrete_sample(probs, self.workload_size)

    def done(self):
        return self.generated >= self.workload_size

    def generate_next(self):
        ops_index = self.ops_sample[self.generated]
        proto = self.ops[ops_index]["proto"]

        # Generate the workload data here.
        built_op = deepcopy(proto)
        loadutils.expand_prototype(built_op)

        self.workload_data.append(built_op)

        self.generated += 1

    def flush_to_disk(self):
        self.workload_file.write(
            json.dumps(self.workload_data, sort_keys=True,
                       indent=4, separators=(', ', ': '))
        )
        self.workload_file.close()
