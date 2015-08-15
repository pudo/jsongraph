from StringIO import StringIO

from rdflib.plugins.serializers.n3 import N3Serializer


def query_header(graph):
    """ Declare namespace bindings for SPARQL queries. """
    sio = StringIO()
    N3Serializer(graph).serialize(sio)
    return sio.getvalue()
