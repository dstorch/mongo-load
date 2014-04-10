###########################################################
#
# Responsible for initializing the load test.
#
###########################################################

from copy import deepcopy
from pymongo import MongoClient, errors, ASCENDING, DESCENDING
from src import loadutils

class LoadTestInitializer:

    # The number of documents in the test collection that have been generated so far.
    generated = 0

    def __init__(self, docs, indices, params):
        if len(docs) == 0:
            print "Warning: empty 'docs' array. Your test collection will be empty."

        if len(indices) == 0:
            print "Warning: empty 'indices' aray. Your test collection will have no indices."

        # Validate 'docs'.
        for el in docs:
            if not isinstance(el, dict):
                raise ValueError("Fatal: all elements of 'docs' must be subdocuments.")
            if len(el) != 2:
                raise ValueError("Fatal: elements of 'docs' must contain exactly two fields.")
            if "proto" not in el:
                raise ValueError("Fatal: missing 'proto' field found in 'docs' array.")
            if "prob" not in el:
                raise ValueError("Fatal: missing 'prob' field found in 'docs' array.")

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

        # Drop the collection, in case it already exists.
        self.test_collection.drop()

        # Sample from the discrete probability distribution defined by the "prob"
        # values in the doc array
        probs = [float(d["prob"]) for d in docs]
        self.doc_sample = loadutils.discrete_sample(probs, self.params.collsize)

    def build_indices(self):
        for index in self.indices:
            if not isinstance(index, dict):
                raise ValueError("Fatal: all index specs must be subobjects.")

            keydir_pairs = []
            for field in index:
                direction = int(index[field])
                if direction != 1 and direction != -1:
                    raise ValueError("Fatal: index direction must be either "
                                     + "1 (ascending) or -1 (descending)");
                pair = (field, (ASCENDING if direction == 1 else DESCENDING))
                keydir_pairs.append(pair)

            self.test_collection.ensure_index(keydir_pairs)

    def done(self):
        return self.generated >= self.params.collsize

    def generate_next(self):
        docs_index = self.doc_sample[self.generated]
        proto = self.docs[docs_index]["proto"]

        # Generate the random data here.
        to_insert = deepcopy(proto)
        loadutils.expand_prototype(to_insert)

        # Give the doc an _id and send it to mongod.
        to_insert["_id"] = self.generated
        self.test_collection.insert(to_insert)

        self.generated += 1
