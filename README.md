mongo-load
==========

Load tester for MongoDB

## Usage

The input to mongo-load is a _load config_ file. This is a JSON configuration file which specifies a load test. Build out a load config according to the following steps.

### Step 1: Specify your data

Specify the structure of your collection using one or more _prototype documents_. An example prototype document might look like this:

```javascript
{
   species: {"@oneOf": ["leopard", "tiger", "lion"]},
   age: {"@uniform": {start: 0, end: 30, type: "int"}},
   height: {"@normal": {mu: 24, sigma: 2, type: "float"}}
}
```

Each prototype document is assigned a _prototype probability_ in [0, 1] such that the probabilities for the prototypes sum to 1. Then, mongo-perf generates the collection data by choosing a prototype according to the prototype probability distribution, constructing a document according to the prototype, and then inserting it into a test mongod instance.

### Step 2: Specify your indices

You must provide mongo-load with a list of indices to build on the test collection prior to the load test. For example:

```javascript
[{species: 1, age: 1}, {height: -1}]
```

### Step 3: Specify your workload

Specify the structure of your collection using one or more _prototype operations_. An example prototype op doc might look like this:

```javascript
{
   query: {height: {$gt: {"@normal": {mu: 24, sigma: 2, type: "float"}}}},
   projection: {"@uniform": {start: 0, end: 30}}
}
```

Like a prototype document, each prototype operation is assigned a probability. A prototype operation can be a query, insert, update, or remove.

### Step 4: Specify parameters

There are a few remaining parameters that you can specify:
* collectionName
* collectionSize
* mongodHost
* mongodPort
* concurrency

## Example Load Config

Putting everything together, here is a complete example load config:

```javascript
{
   collectionName: "cats",
   collectionSize: 10000,
   mongodHost: "catserver.mongodb.com",
   mongodPort: 27017,
   indices: [{species: 1, age: 1}, {height: -1}],
   docs: [
      {proto:
         {
            species: {"@oneOf": ["leopard", "tiger", "lion"]},
            age: {"@uniform": {start: 0, end: 30}},
            height: {"@normal": {mu: 24, sigma: 2}}
         },
       prob: 1}
   ],
   ops: [   
      {proto:
         {
            query: {height: {$gt: {"@normal": {mu: 24, sigma: 2}}}},
            projection: {"@uniform": {start: 0, end: 30}}
          }
       prob: 1}
   ]
}

```

## Requirements

TODO
