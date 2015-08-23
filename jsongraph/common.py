from rdflib import URIRef, RDF
from sparqlquery import Select, v, desc

from jsongraph.query import Query, QueryNode
from jsongraph.binding import Binding


class GraphOperations(object):
    """ Common operations for both the context graphs and the main store. """

    def get_binding(self, schema, data):
        """ For a given schema, get a binding mediator providing links to the
        RDF terms matching that schema. """
        schema = self.parent.get_schema(schema)
        return Binding(schema, self.parent.resolver, data=data)

    def get(self, id, depth=3, schema=None):
        """ Construct a single object based on its ID. """
        uri = URIRef(id)
        if schema is None:
            for o in self.graph.objects(subject=uri, predicate=RDF.type):
                schema = self.parent.get_schema(str(o))
                if schema is not None:
                    break
        else:
            schema = self.parent.get_schema(schema)
        binding = self.get_binding(schema, None)
        return self._objectify(uri, binding, depth=depth, path=set())

    def all(self, schema_name, depth=3):
        schema_uri = self.parent.get_uri(schema_name)
        uri = URIRef(schema_uri)
        var = v['uri']
        q = Select([var]).where((var, RDF.type, uri))
        q = q.order_by(desc(var))
        for data in q.execute(self.graph):
            yield self.get(data['uri'], depth=depth, schema=schema_uri)

    def _objectify(self, node, binding, depth, path):
        """ Given an RDF node URI (and it's associated schema), return an
        object from the ``graph`` that represents the information available
        about this node. """
        if binding.is_object:
            obj = {}
            if binding.parent is None:
                obj['$schema'] = binding.path
            for (s, p, o) in self.graph.triples((node, None, None)):
                prop = binding.get_property(p)
                if prop is None or depth <= 1 or o in path:
                    continue
                # This is slightly odd but yield purty objects:
                if depth <= 2 and (prop.is_array or prop.is_object):
                    continue
                sub_path = path.union([node])
                value = self._objectify(o, prop, depth - 1, sub_path)
                if prop.is_array and prop.name in obj:
                    obj[prop.name].extend(value)
                else:
                    obj[prop.name] = value
            return obj
        elif binding.is_array:
            for item in binding.items:
                return [self._objectify(node, item, depth, path)]
        else:
            return node.toPython()

    def query(self, q):
        """ Run a query using the jsongraph query dialect. This expects an
        input query, which can either be a dict or a list. """
        return Query(self, None, QueryNode(None, None, q))
