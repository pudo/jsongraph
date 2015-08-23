from unittest import TestCase

from jsongraph.graph import Graph

from .util import make_test_graph, resolver
from .util import PERSON_URI, MEM_URI


class RegistryTestCase(TestCase):

    def setUp(self):
        super(RegistryTestCase, self).setUp()
        self.graph = make_test_graph()

    def test_construct(self):
        graph = Graph()
        assert 'github.io' in graph.base_uri, graph.base_uri
        assert graph.get_schema('foo') is None, graph.get_schema('foo')
        assert graph.get_schema({}) == {}, graph.get_schema({})
        assert 'github.io' in repr(graph), repr(graph)
        assert str(graph) in repr(graph), repr(graph)

    def test_register(self):
        assert self.graph.resolver == resolver, self.graph
        assert 'membership' not in self.graph.aliases
        self.graph.register('membership', MEM_URI)
        assert 'membership' in self.graph.aliases

        data = {"id": 'http://foo.bar'}
        self.graph.register('bar', data)
        assert self.graph.get_uri('bar') == data['id'], \
            self.graph.get_uri('bar')
        assert self.graph.get_schema('bar') == data, \
            self.graph.get_schema('bar')

    def test_get_uri(self):
        assert self.graph.resolver == resolver, self.graph
        assert 'person' in self.graph.aliases
        assert self.graph.get_uri('person') == PERSON_URI, \
            self.graph.get_uri('person')

    def test_get_schema(self):
        schema1 = self.graph.get_schema('person')
        schema2 = self.graph.get_schema(PERSON_URI)
        assert schema1 == schema2
        assert 'id' in schema1
        assert schema1['id'] == PERSON_URI, schema1['id']

    def test_resolver(self):
        assert self.graph.resolver.resolution_scope in self.graph.base_uri

    def test_graph(self):
        g = self.graph.graph
        assert g.store == self.graph.store, g.store
        assert g.identifier == self.graph.base_uri, g.identifier
