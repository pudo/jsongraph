import url
from rdflib import ConjunctiveGraph, URIRef


def is_url(text):
    """ Check if the given text looks like a URL. """
    if text is None:
        return False
    text = text.lower()
    return text.startswith('http://') or text.startswith('https://') or \
        text.startswith('urn:') or text.startswith('file://')


def safe_uriref(text):
    """ Escape a URL properly. """
    url_ = url.parse(text).sanitize().deuserinfo().canonical()
    return URIRef(url_.punycode().unicode())


def sparql_store(query_url, update_url):
    gs = ConjunctiveGraph('SPARQLUpdateStore')
    gs.open((query_url, update_url))
    return gs.store


class GraphException(Exception):
    pass
