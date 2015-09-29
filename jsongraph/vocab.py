from uuid import uuid4

from rdflib import URIRef, Namespace

PRED = Namespace('urn:p:')
META = Namespace('urn:meta:')
ID = Namespace('urn:id:')


def BNode():
    return URIRef(uuid4().urn)
