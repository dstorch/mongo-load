mongo-load
==========

Load tester for MongoDB

## Usage

The input to mongo-load is a _load config_ file. This is a JSON configuration file which specifies
a load test. Build out a load config according to the following steps.

### Step 1: Specify your data

Specify the structure of your collection using one or more _prototype documents_.
An example prototype document might look like this:

```javascript
{
"species": {"@oneOf": ["leopard", "tiger", "lion"]},
"age": {"@uniform": {"start": 0, "end": 30, "type": "int"}},
"height": {"@normal": {"mu": 24, "sigma": 2, "type": "float"}}
}
```

Each prototype document is assigned a _prototype probability_ in [0, 1] such that the probabilities
for the prototypes sum to 1. Then, mongo-perf generates the collection data by choosing a prototype
according to the prototype probability distribution, constructing a document according to the
prototype, and then inserting it into a test mongod instance.

### Step 2: Specify your indices

You must provide mongo-load with a list of indices to build on the test collection prior to the
load test. For example:

```javascript
[{"species": 1, "age": 1}, {"height": -1}, {"breed": 1}]
```

### Step 3: Specify your workload

Specify the structure of your collection using one or more _prototype operations_. An example
prototype op doc might look like this:

```javascript
{
"query": {"height": {"$gt": {"@normal": {"mu": 24, "sigma": 2, "type": "int"}}}},
"projection": {"_id": 0, "species": 1, "age": 1}
}
```

Like a prototype document, each prototype operation is assigned a probability.
A prototype operation can be a query, insert, update, or remove.

### Step 4: Specify parameters

There are a few remaining parameters that you can optionally specify:
* dbName - the name of the test database (defaults to "mongoload")
* collectionName - the name of the test collection (defaults to "loadtest")
* collectionSize - the number of documents to insert into the test collection (defaults to 1000)
* mongodHost - the hostname where the test mongod instance is running (defaults to "localhost")
* mongodPort - the port on which the test mongod instance is running (defaults to 27017)
* concurrency - the number of concurrent pymongo clients to run
* workloadSize - the total number of CRUD operations to run across all clients (defaults to 1000)
* workloadDir - the name of the directory that will be created in order to store workload files (defaults to "workloads")

## Example Load Config

Putting everything together, here is a complete example load config:

```javascript
{
   "collectionName": "cats2",
   "collectionSize": 10000,
   "mongodHost": "localhost",
   "mongodPort": 27017,
   "concurrency": 2,
   "workloadSize": 1000,

   "indices": [
      {"species": 1, "age": 1},
      {"height": -1},
      {"breed": 1}
   ],

   "docs": [
      {"proto":
         {
            "species": {"@oneOf": ["leopard", "tiger", "lion"]},
            "age": {"@uniform": {"start": 0, "end": 30, "type": "int"}},
            "height": {"@normal": {"mu": 24, "sigma": 2, "type": "float"}}
         },
       "prob": 0.4
      },
      {"proto":
         {
            "breed": {"@oneOf": ["persian", "balinese", "bengal"]},
            "age": {"@uniform": {"start": 0, "end": 15, "type": "int"}},
            "height": {"@normal": {"mu": 10, "sigma": 4, "type": "float"}},
            "checkups": {"@array": {"maxSize": 10, "docs":
                {"day": {"@uniform": {"start": 0, "end": 6, "type": "int"}},
                 "time": {"@oneOf": ["morning", "afternoon"]}}}}
         },
       "prob": 0.6
      }
   ],

   "ops": [
      {"proto":
         {
            "query": {"_id": {"@uniform": {"start": 0, "end": 10000, "type": "int"}}}
         },
       "prob": 0.4
      },
      {"proto":
         {
            "query": {"height": {"$gt": {"@normal": {"mu": 24, "sigma": 2, "type": "int"}}}},
            "projection": {"_id": 0, "species": 1, "age": 1}
         },
       "prob": 0.4
      },
      {"proto":
         {
            "update": {"_id": {"@uniform": {"start": 0, "end": 11000, "type": "int"}}},
            "spec": {"$set": {"species": {"@oneOf": ["cheetah", "jaguar"]}}},
            "upsert": true
         },
       "prob": 0.2
      }
   ]
}
```

## Requirements

Python with the numpy and pymongo packages is required. Recommended versions are as follows:

* Python >= 2.7.5
* numpy >= 1.6.2
* pymongo >= 2.7
