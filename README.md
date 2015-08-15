# jsongraph [![Build Status](https://travis-ci.org/pudo/jsongraph.svg?branch=master)](https://travis-ci.org/pudo/jsongraph)

This library provides tools to ntegrate data from multiple sources into a
coherent data model. Given a heterogeneous set of source records, it will
generate a set of composite entities with merged information from all
available sources. Further, it allows querying the resulting graph using a
simple, JSON-based graph query language.

The intent of this tool is to make a graph-based data integration system
(based on RDF) seamlessly available through simple JSON objects.

## API

This is what using the library should look like in an ideal scenario:

```python
from jsongraph import Graph

graph = Graph(base_uri='file:///path/to/schema/files')
context = graph.context()
context.add('person_schema.json', data)

uri = 'urn:prod'
graph.consolidate(uri)
res = graph.query([{"name": None, "limit": 5}])
```

## Design

Provenance

Context
    add_object
    remove_object
    remove_all

Graph
    resolver
    registry / types
    store
    graph

    context()
    simplify()
    query()
    entities

Entities
    fingerprint()

#### TODOs:

* Graph load step
* Graph updates
* Graph consolidation

### De-duplication

Generate a set of descriptors of the form outlined below, then

{
    "fingerprint": "...",
    "entity": "...",
    "data": {

    },
    "source": {
        "label": "...",
        "url": "http://..."
    }
}


## Tests

The test suite will usually be executed in it's own ``virtualenv`` and perform a
coverage check as well as the tests. To execute on a system with ``virtualenv``
and ``make`` installed, type:

```bash
$ make test
```
