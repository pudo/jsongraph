import json
from rdflib import ConjunctiveGraph
from unittest import TestCase

from jsongraph.load import load_obj

from .util import resolver, fixture_file
from .util import PERSON_URI, ORG_URI


class ConverterTestCase(TestCase):

    def setUp(self):
        super(ConverterTestCase, self).setUp()
        self.data = json.load(fixture_file('rdfconv/bt_partial.json'))
        _, self.person_schema = resolver.resolve(PERSON_URI)
        _, self.org_schema = resolver.resolve(ORG_URI)

    def test_basic_load_data(self):
        ng = ConjunctiveGraph()
        for org in self.data['organizations']:
            ctx_id = load_obj(ng, org, self.org_schema, resolver)
            # g = ng.get_context(ctx_id)
            # print g
            # print len(list(g.triples((None, None, None))))
            # assert False
        # print len(list(ng.triples((None, None, None))))
        # assert False
