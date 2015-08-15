from unittest import TestCase

from jsongraph.graph import Graph

from .util import resolver
from .util import PERSON_URI, MEM_URI, ORG_URI


class RegistryTestCase(TestCase):

    def setUp(self):
        super(RegistryTestCase, self).setUp()
        self.graph = Graph(resolver=resolver)
        self.graph.register('person', PERSON_URI)
        self.graph.register('organization', ORG_URI)

    def test_register(self):
        assert self.graph.resolver == resolver, self.graph
        assert 'membership' not in self.graph.aliases
        self.graph.register('membership', MEM_URI)
        assert 'membership' in self.graph.aliases

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
