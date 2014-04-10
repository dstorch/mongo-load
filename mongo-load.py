import json
import sys
import os.path

from src import loadtest

def main():
    if not len(sys.argv) == 2:
        print "mongo-load: MongoDB load tester. Usage:\n"
        print "python mongo-load.py <load config>.json"
        sys.exit(1)

    filename = sys.argv[1];
    if not os.path.isfile(filename):
        print "Fatal: file does not exist: " + filename
        sys.exit(1)

    filehandle = open(filename, "r")
    confdata = json.load(filehandle)

    try:
        load_test = loadtest.LoadTest(confdata)
        load_test.init_collection()
    except ValueError as e:
        print e
        sys.exit(1)

if __name__ == "__main__":
    main()
