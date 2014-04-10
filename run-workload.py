import json
import sys
from pymongo import MongoClient
from argparse import ArgumentParser


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
        if "query" in entry:
            query = entry["query"]
            proj = {}
            if "projection" in entry:
                proj = entry["projection"]

            cursor = coll.find(query, proj)
            count = 0
            for res in cursor:
                count += 1


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
