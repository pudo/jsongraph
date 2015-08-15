from unittest import TestCase

from jsongraph.registry import SchemaRegistry

from .util import resolver, fixture_uri
from .util import PERSON_URI, MEM_URI, ORG_URI


class RegistryTestCase(TestCase):

    def setUp(self):
        super(RegistryTestCase, self).setUp()
        self.reg = SchemaRegistry(resolver)
        self.reg.register('person', PERSON_URI)
        self.reg.register('organization', ORG_URI)

    def test_register(self):
        assert self.reg.resolver == resolver, self.reg
        assert 'membership' not in self.reg.aliases
        self.reg.register('membership', MEM_URI)
        assert 'membership' in self.reg.aliases

    def test_get_uri(self):
        assert self.reg.resolver == resolver, self.reg
        assert 'person' in self.reg.aliases
        assert self.reg.get_uri('person') == PERSON_URI, \
            self.reg.get_uri('person')

    def test_get_schema(self):
        schema1 = self.reg.get_schema('person')
        schema2 = self.reg.get_schema(PERSON_URI)
        assert schema1 == schema2
        assert 'id' in schema1
        assert schema1['id'] == PERSON_URI, schema1['id']
