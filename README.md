# jsongraph [![Build Status](https://travis-ci.org/pudo/jsongraph.svg?branch=master)](https://travis-ci.org/pudo/jsongraph)

This library provides tools to ntegrate data from multiple sources into a coherent
data model. Given a heterogeneous set of source records, it will generate a set
of composite entities with merged information from all available sources. Further,
it allows querying the resulting graph using a simple, JSON-based graph
query language.

## API

This is what using the library should look like in an ideal scenario:

```python
from jsongraph import Graph

graph = Graph(base_uri='file:///path/to/schema/files')
context = graph.context()
context.add_object(data)
context.apply()

uri = 'urn:test:prod'
graph.consolidate(uri)
res = graph.query([{"name": None, "limit": 5}])
```

## Tests

The test suite will usually be executed in it's own ``virtualenv`` and perform a
coverage check as well as the tests. To execute on a system with ``virtualenv``
and ``make`` installed, type:

```bash
$ make test
```
