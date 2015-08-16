import json
from unittest import TestCase

from ..util import make_test_graph, fixture_file


class ContextTestCase(TestCase):

    def setUp(self):
        super(ContextTestCase, self).setUp()
        self.data = json.load(fixture_file('rdfconv/bt_partial.json'))
        self.graph = make_test_graph()
        self.context = self.graph.context()
        for org in sorted(self.data['organizations']):
            self.context.add('organization', org)
        for per in sorted(self.data['persons']):
            self.context.add('person', per)

    def test_basic_query(self):
        res = self.context.query({'limit': 1})
        assert res['status'] == 'ok'
