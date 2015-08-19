from rdflib import URIRef
from rdflib.namespace import RDF

from jsongraph.binding import Binding


class Converter(Binding):

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
