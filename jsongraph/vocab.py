from uuid import uuid4

from rdflib import URIRef, Namespace

PRED = Namespace('/data/fields/')
META = Namespace('/meta/')
ID = Namespace('/data/id/')


def BNode():
    return URIRef(uuid4().urn)
