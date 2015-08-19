from uuid import uuid4

from rdflib import URIRef, Namespace

PRED = Namespace('urn:fields:')
META = Namespace('urn:meta:')
ID = Namespace('urn:id:')


def BNode():
    return URIRef(uuid4().urn)
