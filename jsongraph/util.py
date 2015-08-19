from StringIO import StringIO

from rdflib import ConjunctiveGraph
from rdflib.plugins.serializers.n3 import N3Serializer


def query_header(graph):
    """ Declare namespace bindings for SPARQL queries. """
    sio = StringIO()
    N3Serializer(graph).serialize(sio)
    return sio.getvalue()


def sparql_store(query_url, update_url):
    gs = ConjunctiveGraph('SPARQLUpdateStore')
    gs.open((query_url, update_url))
    return gs.store
