import json
import sys
from pymongo import MongoClient
from argparse import ArgumentParser
from src import loadutils


def parse_arguments():
    parser = ArgumentParser(description="Runs a mongo-load workload file")

    parser.add_argument("-f", dest="workload_file", default=None,
                        help="Workload file to run")
    parser.add_argument("-m", dest="mongod_host", default="localhost",
                        help="Hostname of the mongod instance")
    parser.add_argument("-p", dest="mongod_port", default=27017, type=int,
                        help="Port on which to connect to mongod")
    parser.add_argument("-d", dest="dbname", default="mongoload",
                        help="Database containing the test collection")
    parser.add_argument("-c", dest="collname", default="loadtest",
                        help="Name of the test collection")

    return parser.parse_known_args()


def run_workload(coll, workload_data):
    for entry in workload_data:

        #
        # Handle each CRUD operation in turn.
        #

        # Queries
        if "query" in entry:
            query = entry["query"]

            proj = {}
            if "projection" in entry:
                proj = entry["projection"]

            limit = 0
            if "limit" in entry:
                 limit = entry["limit"]

            skip = 0
            if "skip" in entry:
                skip = entry["skip"]

            cursor = coll.find(query, proj)
            if "limit" in entry:
                cursor = cursor.limit(entry["limit"])
            if "skip" in entry:
                cursor = cursor.limit(entry["skip"])
            if "sort" in entry:
                kp = loadutils.convert_keypattern(entry["sort"])
                cursor = cursor.sort(kp)

            # Run the query to completion.
            count = 0
            for res in cursor:
                count += 1

        # Updates
        elif "update" in entry:
            multi = False
            if "multi" in entry:
                multi = entry["multi"]
            upsert = False
            if "upsert" in entry:
                upsert = entry["upsert"]
            coll.update(entry["update"], entry["spec"], upsert=upsert, multi=multi)

        # Inserts
        elif "insert" in entry:
            coll.insert(entry["insert"])

        # Removes
        elif "remove" in entry:
            multi = True
            if "multi" in entry:
                multi = entry["multi"]
            coll.remove(entry["remove"], multi=multi)


def main():
    args, extra_args = parse_arguments()

    # Get test collection.
    client = MongoClient(args.mongod_host, args.mongod_port)
    db = client[args.dbname]
    coll = db[args.collname]

    # Get the test workload.
    workload_file = open(args.workload_file, "r")
    workload_data = json.load(workload_file)

    run_workload(coll, workload_data)

if __name__ == "__main__":
    main()
