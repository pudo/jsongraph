from StringIO import StringIO

from rdflib import ConjunctiveGraph


def sparql_store(query_url, update_url):
    gs = ConjunctiveGraph('SPARQLUpdateStore')
    gs.open((query_url, update_url))
    return gs.store
