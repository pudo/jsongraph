from rdflib import Literal, URIRef
# from rdflib.namespace import RDF

from jsonmapping import SchemaVisitor

from jsongraph import uri
from jsongraph.vocab import BNode, PRED, ID


class Binding(SchemaVisitor):

    @property
    def uri(self):
        val = self.path
        return None if val is None else URIRef(val)

    @property
    def subject(self):
        subject = self.schema.get('rdfSubject', 'id')
        for prop in self.properties:
            if prop.match(subject):
                return prop.object

        if not hasattr(self, '_bnode'):
            self._bnode = BNode()
        return self._bnode

    @property
    def predicate(self):
        return URIRef(PRED[self.name])

    @property
    def reverse(self):
        name = self.schema.get('rdfReverse')
        if name is not None:
            return PRED[name]

    def get_property(self, predicate):
        for prop in self.properties:
            if predicate == prop.predicate:
                return prop

    @property
    def object(self):
        if self.schema.get('format') == 'uri' or \
                self.schema.get('rdfType') == 'uri':
            return URIRef(uri.make_safe(self.data))
        if self.schema.get('rdfType') == 'id' and not uri.check(self.data):
            return ID[self.data]
        return Literal(self.data)
