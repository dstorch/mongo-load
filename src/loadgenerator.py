###########################################################
#
# Creates a test workload and writes it to a file.
#
###########################################################

from copy import deepcopy
from src import loadutils
from subprocess import Popen
from os import path, remove
import json
import sys

class WorkloadGenerator:

    generated = 0
    workload_data = []

    def __init__(self, idnum, ops, params):
        if len(ops) == 0:
            print "Warning: empty 'ops' array. No load will be applied."

        # Validate 'ops'.
        for el in ops:
            if not isinstance(el, dict):
                raise ValueError("Fatal: all elements of 'ops' must be subdocuments.")
            if len(el) != 2:
                raise ValueError("Fatal: elements of 'ops' must contain exactly two fields.")
            if "proto" not in el:
                raise ValueError("Fatal: missing 'proto' field found in 'ops' array.")
            if "prob" not in el:
                raise ValueError("Fatal: missing 'prob' field found in 'ops' array.")

            proto = el["proto"]
            if "query" in proto:
                valid_fields = ["query", "projection", "sort", "limit", "skip"]
                for field in proto:
                    if field not in valid_fields:
                        raise ValueError("Fatal: unknown field '" + field + "' in query op.")
            elif "update" in proto:
                valid_fields = ["update", "spec", "multi", "upsert"]

                if "spec" not in proto:
                    raise ValueError("Fatal: missing 'spec' field for update op.")

                for field in proto:
                    if field not in valid_fields:
                        raise ValueError("Fatal: unknown field '" + field + "' in update op.")
            elif "insert" in proto:
                if len(el) != 1:
                    raise ValueError("Fatal: insert ops must have only the 'insert' field.")
            elif "remove" in proto:
                validFields = ["remove", "multi"]
                for field in proto:
                    if field not in valid_fields:
                        raise ValueError("Fatal: unknown field '" + field + "' in remove op.")
            else:
                raise ValueError("Fatal: ops array entry does not contain "
                                 + "'query', 'update', 'insert', or 'remove'.")

        self.idnum = idnum
        self.ops = ops
        self.params = params

        # Generate the path name at which we will store this workload.
        self.workload_path = path.join(params.workload_dir, "workload" + str(idnum))

        if path.exists(self.workload_path):
            sys.stderr.write("Warning: file '" + self.workload_path + "' exists."
                             + " It is being removed.\n")
            remove(self.workload_path)

        self.workload_file = open(self.workload_path, "w")

        # Do the same number of ops regardless of the concurrency factor.
        self.workload_size = params.workload_size / params.concurrency

        # Sample from the discrete probability distribution defined by the "prob"
        # values in the ops array.
        probs = [float(d["prob"]) for d in ops]
        if sum(probs) != 1.0:
            raise ValueError("Fatal: probabilities in 'ops' specification do not add to 1.0")
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

    def spawn_worker(self):
        args = ["python", "run-workload.py"]
        args.extend(["-f", self.workload_path])
        args.extend(["-m", self.params.mongod_host])
        args.extend(["-p", str(self.params.mongod_port)])
        args.extend(["-d", self.params.dbname])
        args.extend(["-c", self.params.collname])
        return Popen(args)
