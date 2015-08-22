# jsongraph [![Build Status](https://travis-ci.org/pudo/jsongraph.svg?branch=master)](https://travis-ci.org/pudo/jsongraph)

This library provides tools to integrate data from multiple sources into a
coherent data model. Given a heterogeneous set of source records, it will
generate a set of composite entities with merged information from all
available sources. Further, it allows querying the resulting graph using a
simple, JSON-based graph query language.

The intent of this tool is to make a graph-based data integration system
(based on RDF) seamlessly available through simple JSON objects.

## Usage

This is what using the library looks like in a simplified scenario:

```python
from jsongraph import Graph

# Create a graph for all project information. This can be backed by a
# triple store or an in-memory construct.
graph = Graph(base_uri='file:///path/to/schema/files')
graph.register('person', 'person_schema.json')

# Load data about a person.
context = graph.context()
context.add('person', data)
context.save()
# Repeat data loading for a variety of source files.

# This will integrate data from all source files into a single representation
# of the data.
context = graph.consolidate('urn:prod')

# Metaweb-style queries:
for item in context.query([{"name": None, "limit": 5}]):
    print item['name']
```

## Design

A ``jsongraph`` application is focussed on a ``Graph``, which stores a set of
data. A ``Graph`` can either exist only in memory, or be stored in a backend
database.

All data in a ``Graph`` is structured as collections of JSON objects (i.e.
nested dictionaries, lists and values). The structure of all stored objects
must be defined using a [JSON Schema](http://json-schema.org/). Some limits
apply to such schema, e.g. they may not allow additional or pattern properties.

### Contexts and Metadata

The objects in each ``Graph`` are grouped into a set of ``Contexts``. Those
also include metadata, such as the source of the data, and the level of trust
that the system shall have in those data. A ``Context`` will usually correspond
to a source data file, or a user interaction.

### Consolidated Contexts

When working with ``jsongraph``, a user will first load data into a variety of
``Contexts``. They can then generate a consolidated version of the data, in a
separate ``Context``.

This consolidated version applies entity de-duplication. For object properties
with multiple available values across several ``Contexts``, the information
from the most trustworthy ``Context`` will be chosen.

### Queries

``jsongraph`` includes a query language implementation, which is heavily
inspired by Google's [Metaweb Query Language](http://mql.freebaseapps.com/ch03.html).
Queries are written as JSON, and search proceeds by example. Searches can also
be deeply nested, traversing the links between objects stored in the ``Graph``
at an arbitrary complexity.

Queries on the data can be run either against any of the source ``Contexts``,
or against the consolidated context. Queries against the consolidated
``Context`` will produce responses which reflect the best available information
based on data from a variety of sources.

### De-duplication

One key part of the functions of this library will be the application of
de-duplication rules. This will take place in three steps:

* Generating a set of de-duplicating candidates for all entities in a given
  ``Graph``. These will be simplified representations of objects which can be
  fed into a comparison tool (either automated or interactive with the user).

* Once the candidates have been decided, they are transformed into a mapping of
  the type (``original_fingerprint`` -> ``same_as_fingerprint``). Such mappings
  are applied to a context.

* Upon graph consolidation (see above), the entities which have been mapped to
  another are not included. All their properties are inherited by the
  destination entity.

A data comparison candidate may look like this:

```json
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
```

## Tests

The test suite will usually be executed in it's own ``virtualenv`` and perform a
coverage check as well as the tests. To execute on a system with ``virtualenv``
and ``make`` installed, type:

```bash
$ make test
```
