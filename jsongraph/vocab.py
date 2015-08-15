from uuid import uuid4

from rdflib import Graph, URIRef, Namespace

PRED = Namespace('/data/fields/')
META = Namespace('/meta/')
ID = Namespace('/data/id/')


def get_graph(graph=None, identifier=None):
    if graph is None:
        graph = Graph(identifier=identifier)
    graph.bind('meta', META)
    graph.bind('pred', PRED)
    graph.bind('id', ID)
    return graph


def BNode():
    return URIRef(uuid4().urn)
