from rdflib import Literal, URIRef
from rdflib.namespace import RDF

from jsonmapping import SchemaVisitor

from jsongraph import uri
from jsongraph.vocab import BNode, PRED, ID


class Converter(SchemaVisitor):

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
        predicate = self.schema.get('rdfPredicate')
        if predicate is None:
            name = self.schema.get('rdfName', self.name)
            predicate = PRED[name]
        return URIRef(predicate)

    @property
    def reverse(self):
        predicate = self.schema.get('rdfReversePredicate')
        if predicate is not None:
            return URIRef(predicate)

        name = self.schema.get('rdfReverseName')
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

    def triplify(self):
        """ Recursively generate RDF statement triples from the data and
        schema supplied to the application. """
        if self.data is None:
            return

        if self.is_object:
            if self.uri:
                self.graph.add((self.subject, RDF.type, self.uri))

            if self.parent is not None:
                parent = self.parent.subject
                if self.parent.is_array:
                    parent = self.parent.parent.subject
                self.graph.add((parent, self.predicate, self.subject))
                if self.reverse is not None:
                    self.graph.add((self.subject, self.reverse, parent))

            for prop in self.properties:
                prop.triplify()

            return self.subject

        elif self.is_array:
            for item in self.items:
                item.triplify()

        else:
            subject = self.parent.subject
            self.graph.add((subject, self.predicate, self.object))
            if self.reverse is not None:
                self.graph.add((self.object, self.reverse, subject))

    def objectify(self, node, depth=3, path=None):
        """ Given an RDF node URI (and it's associated schema), return an
        object from the ``graph`` that represents the information available
        about this node. """
        if path is None:
            path = set()

        if self.is_object:
            obj = {}
            for (s, p, o) in self.graph.triples((node, None, None)):
                prop = self.get_property(p)
                if prop is None or depth <= 1 or o in path:
                    continue
                sub_path = path.union([node])
                value = prop.objectify(o, depth=depth - 1, path=sub_path)
                if prop.is_array and prop.name in obj:
                    obj[prop.name].extend(value)
                else:
                    obj[prop.name] = value
            return obj
        elif self.is_array:
            for item in self.items:
                return [item.objectify(node, depth=depth, path=path)]
        else:
            return node.toPython()

    @property
    def graph(self):
        return self.state

    @classmethod
    def import_data(cls, resolver, graph, data, schema):
        """ Given an object ``data`` and a JSON ``schema`` describing it, load
        the given data into the ``graph`` as a set of RDF statements. """
        obj = cls(schema, resolver, data=data, name=None, state=graph)
        return obj.triplify()

    @classmethod
    def load_schema_uri(cls, resolver, graph, schema, uri, depth=3):
        """ Given a ``uri`` present in ``graph``, return a complete
        representation of the object described in ``schema`` from the graph.
        """
        obj = cls(schema, resolver, name=None, state=graph)
        return obj.objectify(URIRef(uri), depth=depth)

    @classmethod
    def load_uri(cls, resolver, graph, uri, depth=3):
        """ Same as ``load_schema_uri`` but determine the possible schemata
        first, using RDF:type annotations. """
        obj = {}
        for (s, p, o) in graph.triples((URIRef(uri), RDF.type, None)):
            _, schema = resolver.resolve(o)
            if schema is not None:
                obj.update(cls.load_schema_uri(resolver, graph, schema,
                                               uri, depth=depth))
        return obj
