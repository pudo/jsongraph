import url
from rdflib import Literal, URIRef
# from rdflib.term import Identifier
# from rdflib.namespace import RDF

from jsonmapping import SchemaVisitor

from jsongraph.util import is_url, safe_uriref
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
                obj = prop.object
                if not isinstance(obj, URIRef):
                    obj = ID[obj]
                return obj

        if not hasattr(self, '_bnode'):
            self._bnode = BNode()
        return self._bnode

    @property
    def predicate(self):
        return PRED[self.schema.get('rdfName', self.name)]

    @property
    def reverse(self):
        name = self.schema.get('rdfReverse')
        if name is not None:
            return PRED[name]

    def get_property(self, predicate):
        for prop in self.properties:
            if predicate == PRED[prop.name]:
                return prop

    @property
    def object(self):
        if self.schema.get('format') == 'uri' or \
                self.schema.get('rdfType') == 'uri':
            try:
                return safe_uriref(self.data)
            except:
                pass
        if self.schema.get('rdfType') == 'id':
            if is_url(self.data):
                try:
                    return safe_uriref(self.data)
                except:
                    pass
            if not self.data.startswith(ID):
                return ID[self.data]
        return Literal(self.data)
