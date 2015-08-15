import urllib
from datetime import datetime

from rdflib import URIRef, Literal
from rdflib.namespace import RDF

from jsongraph import uri
from jsongraph.vocab import META, BNode, get_graph


class Provenance(object):

    def __init__(self, label=None, url=None, file=None):
        self.label = label
        self.url = url
        self.file = file


def get_context(source_url=None, source_title=None, source_file=None):
    """ Generate a graph with some provenance information attached to it. """
    identifier = None
    if uri.check(source_url):
        identifier = URIRef(uri.make_safe(source_url))
    if identifier is None:
        if source_file is not None:
            identifier = 'file://' + urllib.pathname2url(source_file)
            identifier = URIRef(identifier)
        else:
            identifier = BNode()
    ctx = get_graph(identifier=identifier)
    ctx.add((identifier, RDF.type, META.Provenance))
    if source_url:
        ctx.add((identifier, META.sourceUrl,
                 URIRef(uri.make_safe(source_url))))
    if source_title:
        ctx.add((identifier, META.source, Literal(source_title)))
    if source_file:
        ctx.add((identifier, META.sourceFile, Literal(source_file)))
    ctx.add((identifier, META.created, Literal(datetime.utcnow())))
    return ctx
