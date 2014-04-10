###########################################################
#
# The parsed representation of a load test configuration.
#
###########################################################

from loadinit import LoadTestInitializer
from loadgenerator import WorkloadGenerator
from os import path, mkdir
import sys

class LoadTestConfigParams:

    #
    # Parameter defaults.
    #

    dbname = "mongoload"

    collname = "loadtest"
    collsize = 1000
    cleanup_coll = False

    mongod_host = "localhost"
    mongod_port = 27017

    concurrency = 1
    workload_size = 1000
    workload_dir = "workloads"

    def __init__(self, loadconf):
        if "dbName" in loadconf:
            self.dbname = loadconf["dbName"]
        if "collectionName" in loadconf:
            self.collname = loadconf["collectionName"]
        if "collectionSize" in loadconf:
            self.collsize = loadconf["collectionSize"]
        if "cleanupColl" in loadconf:
            self.cleanup_coll = loadconf["cleanup_coll"]
        if "mongodHost" in loadconf:
            self.mongod_host = loadconf["mongodHost"]
        if "mongodPort" in loadconf:
            self.mongod_port = loadconf["mongodPort"]
        if "concurrency" in loadconf:
            self.concurrency = loadconf["concurrency"]
        if "workloadSize" in loadconf:
            self.workload_size = loadconf["workloadSize"]
        if "workloadDir" in loadconf:
            self.workload_dir = loadconf["workloadDir"]


class LoadTest:

    # Known top-level field names.
    toplevel_fields = [
        "dbName",
        "collectionName",
        "collectionSize",
        "mongodHost",
        "mongodPort",
        "indices",
        "concurrency",
        "workloadSize",
        "workloadDir",
        "docs",
        "ops"
    ]

    def __init__(self, loadconf):
        self.raw_config = loadconf

        # Ensure required fields are present.
        for f in ["docs", "ops", "indices"]:
            if f not in loadconf:
                raise ValueError("Fatal: required config field not found: '" + f + "'.")

        # Ensure required fields are lists.
        for f in ["docs", "ops", "indices"]:
            if not isinstance(loadconf[f], list):
                raise ValueError("Fatal: config field must be an array: '" + f + "'.")

        # Check for unknown fields.
        for f in self.raw_config:
            if f not in self.toplevel_fields:
                raise ValueError("Fatal: unknown config field: '" + f + "'.")

        self.params = LoadTestConfigParams(loadconf)
        self.initializer = LoadTestInitializer(loadconf["docs"], loadconf["indices"], self.params)

        # Create the workload directory, printing a warning if it already exists.
        if path.exists(self.params.workload_dir):
            sys.stderr.write("Warning: directory already exists: "
                             + self.params.workload_dir + "\n")
        else:
            mkdir(self.params.workload_dir)

        self.workloads = []
        for i in range(0, self.params.concurrency):
            self.workloads.append(WorkloadGenerator(i, self.raw_config["ops"], self.params))


    def init_collection(self):
        self.initializer.build_indices()
        while not self.initializer.done():
            self.initializer.generate_next()


    def generate_workloads(self):
        for workload in self.workloads:
            while not workload.done():
                workload.generate_next()
            workload.flush_to_disk()
