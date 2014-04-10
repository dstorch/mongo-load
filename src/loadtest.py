###########################################################
#
# The parsed representation of a load test configuration.
#
###########################################################

from loadinit import LoadTestInitializer

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

    def __init__(self, loadconf):
        if "dbName" in loadconf:
            self.dbname = loadconf["dbName"]
        if "collectionName" in loadconf:
            self.collname = loadconf["collectionName"]
        if "collectionSize" in loadconf:
            self.collsize = loadconf["collectionSize"]
        if "cleanupColl" in loadconf:
            self.cleanup_coll = loadconf["cleanup_coll"]


class LoadTest:

    # Known top-level field names.
    toplevel_fields = [
        "dbName",
        "collectionName",
        "collectionSize",
        "mongodHost",
        "mongodPort",
        "indices",
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

    def init_collection(self):
        self.initializer.build_indices()
        while not self.initializer.done():
            self.initializer.generate_next()


