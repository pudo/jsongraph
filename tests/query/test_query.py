import json
from unittest import TestCase

from ..util import make_test_graph, fixture_file

CTX = {}

def get_context():
    if 'ctx' not in CTX:
        data = json.load(fixture_file('rdfconv/bt_partial.json'))
        graph = make_test_graph()
        context = graph.context()
        for org in sorted(data['organizations']):
            context.add('organization', org)
        for per in sorted(data['persons']):
            context.add('person', per)
        CTX['ctx'] = context
    return CTX['ctx']


class ContextTestCase(TestCase):

    def setUp(self):
        super(ContextTestCase, self).setUp()

    def test_basic_query(self):
        context = get_context()
        res = context.query({'limit': 100, 'name': None}).results()
        assert res['status'] == 'ok', res
        assert res['query']['limit'] == 1, res
        assert res['result']['name'] is not None, res

    def test_list_query(self):
        context = get_context()
        res = context.query([{'id': None, 'name': None}]).results()
        assert res['status'] == 'ok'
        assert len(res['result']) == 15
        fst = res['result'][0]
        assert 'id' in fst, fst
        assert 'name' in fst, fst

    def test_nested_query(self):
        context = get_context()
        res = context.query({
            'memberships': [{
                'organization': {'name': "CSU", "id": None}
            }],
            'contact_details': []
        }).results()
        assert res['status'] == 'ok'
        # from pprint import pprint
        # pprint(res)
        # assert len(res['result']) > 0
