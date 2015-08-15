from rdflib import ConjunctiveGraph

from jsongraph.converter import Converter
from jsongraph.provenance import get_context


def load_obj(graph, obj, schema, resolver):
    cache = get_context()
    Converter.import_data(resolver, cache, obj, schema)
    # print len(list(cache.triples((None, None, None))))
    # print cache.serialize(format='nt')
    # print cache.identifier, type(cache.identifier)

    query = 'CLEAR GRAPH %s ; INSERT DATA { GRAPH %s { %s }} ; '
    query = query % (cache.identifier.n3(),
                     cache.identifier.n3(),
                     cache.serialize(format='nt'))
    # print query
    graph.update(query)
    return cache.identifier
