from nose.tools import raises
from unittest import TestCase

from jsongraph.graph import Graph
from jsongraph.util import GraphException

from .util import make_test_graph, resolver
from .util import PERSON_URI, MEM_URI


class GraphTestCase(TestCase):

    def setUp(self):
        super(GraphTestCase, self).setUp()
        self.graph = make_test_graph()

    @raises(GraphException)
    def test_missing_schema(self):
        graph = Graph()
        graph.get_schema('foo')

    def test_graph(self):
        graph = Graph()
        assert 'github.io' in graph.base_uri, graph.base_uri
        assert graph.get_schema({}) == {}, graph.get_schema({})
        assert 'github.io' in repr(graph), repr(graph)
        assert str(graph) in repr(graph), repr(graph)

    def test_graph_unconfigured(self):
        graph = Graph()
        assert graph.base_uri is not None
        assert graph.resolver is not None

    @raises(GraphException)
    def test_invalid_schema_config(self):
        Graph(config={'schemas': 5})

    @raises(GraphException)
    def test_invalid_store_config(self):
        Graph(config={'store': {'update': 6, 'query': 'huhu'}})

    def test_graph_sparql(self):
        config = {
            'store': {
                'query': 'http://localhost:3030/gk-test/query',
                'update': 'http://localhost:3030/gk-test/update'
            }
        }
        graph = Graph(config=config)
        assert graph.store is not None, graph.store
        assert 'SPARQLUpdateStore' in repr(graph.store), graph.store
        assert graph.buffered is True, graph.buffered

    def test_register(self):
        assert self.graph.resolver == resolver, self.graph
        assert 'memberships' not in self.graph.aliases
        self.graph.register('memberships', MEM_URI)
        assert 'memberships' in self.graph.aliases

        data = {"id": 'http://foo.bar'}
        self.graph.register('bar', data)
        assert self.graph.get_uri('bar') == data['id'], \
            self.graph.get_uri('bar')
        assert self.graph.get_schema('bar') == data, \
            self.graph.get_schema('bar')

    def test_get_uri(self):
        assert self.graph.resolver == resolver, self.graph
        assert 'persons' in self.graph.aliases
        assert self.graph.get_uri('persons') == PERSON_URI, \
            self.graph.get_uri('persons')

    def test_get_schema(self):
        schema1 = self.graph.get_schema('persons')
        schema2 = self.graph.get_schema(PERSON_URI)
        assert schema1 == schema2
        assert 'id' in schema1
        assert schema1['id'] == PERSON_URI, schema1['id']

    def test_resolver(self):
        assert self.graph.resolver.resolution_scope in self.graph.base_uri

    def test_graph_store(self):
        g = self.graph.graph
        assert g.store == self.graph.store, g.store
        assert g.identifier == self.graph.base_uri, g.identifier
