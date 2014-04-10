###########################################################
#
# Responsible for initializing the load test.
#
###########################################################

from pymongo import MongoClient, errors

class LoadTestInitializer:

    # The number of documents in the test collection that have been generated so far.
    generated = 0

    def __init__(self, docs, indices, params):

        if len(docs) == 0:
            print "Warning: empty 'docs' array. Your test collection will be empty."

        if len(indices) == 0:
            print "Warning: empty 'indices' aray. Your test collection will have no indices."

        self.docs = docs
        self.indices = indices
        self.params = params

        # Try connecting to mongod instance.
        try:
            self.client = MongoClient(params.mongod_host, params.mongod_port)
            self.test_db = self.client[params.dbname]
            self.test_collection = self.test_db[params.collname]
        except errors.ConnectionFailure:
            raise ValueError("Fatal: could not connect to test mongod: "
                             + params.mongod_host + ":" + str(params.mongod_port))

    def done(self):
        return self.generated >= self.params.collsize

    def generate_next(self):
        # TODO
        self.generated += 1
        return self.generated
