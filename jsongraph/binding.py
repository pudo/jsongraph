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
        if not hasattr(self, '_rdf_subject'):
            self._rdf_subject = None
            subject = self.schema.get('rdfSubject', 'id')
            for prop in self.properties:
                if prop.match(subject):
                    obj = prop.object
                    if obj is not None and not isinstance(obj, URIRef):
                        obj = ID[obj]
                    self._rdf_subject = obj
                    break
            if self._rdf_subject is None:
                self._rdf_subject = BNode()
        return self._rdf_subject

    @property
    def predicate(self):
        return PRED[self.schema.get('rdfName', self.name)]

    @property
    def reverse(self):
        name = self.schema.get('rdfReverse')
        if name is not None:
            return PRED[name]
        if self.parent is not None and self.parent.is_array:
            return self.parent.reverse

    def get_property(self, predicate):
        for prop in self.properties:
            if predicate == PRED[prop.name]:
                return prop

    @property
    def object(self):
        if self.data is None:
            return self.data
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
            return ID[self.data]
        return Literal(self.data)
