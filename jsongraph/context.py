from rdflib import Graph, URIRef
# from jsonschema import validate

from jsongraph.vocab import BNode
from jsongraph.metadata import MetaData
from jsongraph.common import GraphOperations
from jsongraph.triplify import triplify


class Context(GraphOperations):

    def __init__(self, parent, identifier=None, meta=None):
        self.parent = parent
        if identifier is None:
            identifier = BNode()
        self.identifier = URIRef(identifier)
        self.meta = MetaData(self, meta)
        self.meta.generate()

    @property
    def graph(self):
        if not hasattr(self, '_graph') or self._graph is None:
            if self.parent.buffered:
                self._graph = Graph(identifier=self.identifier)
            else:
                self._graph = self.parent.graph.get_context(self.identifier)
        return self._graph

    def add(self, schema, data):
        """ Stage ``data`` as a set of statements, based on the given
        ``schema`` definition. """
        binding = self.get_binding(schema, data)
        uri, triples = triplify(binding)
        for triple in triples:
            self.graph.add(triple)
        return uri

    def save(self):
        """ Transfer the statements in this context over to the main store. """
        if self.parent.buffered:
            query = """
                INSERT DATA { GRAPH %s { %s } }
            """
            query = query % (self.identifier.n3(),
                             self.graph.serialize(format='nt'))
            self.parent.graph.update(query)
            self.flush()
        else:
            self.meta.generate()

    def delete(self):
        """ Delete all statements matching the current context identifier
        from the main store. """
        if self.parent.buffered:
            query = 'CLEAR SILENT GRAPH %s ;' % self.identifier.n3()
            self.parent.graph.update(query)
            self.flush()
        else:
            self.graph.remove((None, None, None))

    def flush(self):
        """ Clear all the pending statements in the local context, without
        transferring them to the main store. """
        self._graph = None

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return '<Context("%s")>' % self.identifier
