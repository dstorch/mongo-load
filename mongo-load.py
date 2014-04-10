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
        print "Initializing test collection..."
        load_test.init_collection()
        print "Generating workloads..."
        load_test.generate_workloads()
        print "Running test..."
        elapsed = load_test.run()
        print "Total time (ms): ", elapsed
    except ValueError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)

    print "Test complete."

if __name__ == "__main__":
    main()
