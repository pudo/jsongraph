import json
from unittest import TestCase

from .util import make_test_graph, fixture_file

CTX = {}


def get_context():
    if 'ctx' not in CTX:
        data = json.load(fixture_file('rdfconv/bt_partial.json'))
        graph = make_test_graph()
        context = graph.context()
        for org in sorted(data['organizations']):
            context.add('organizations', org)
        for per in sorted(data['persons']):
            context.add('persons', per)
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
        assert len(res['result']) > 0

    def test_query_multiple(self):
        context = get_context()
        q = [{'id': None, 'limit': 2, 'memberships': [
            {'id': None, 'organization': {'name': None}}
        ]}]
        res = context.query(q).results()
        assert res['status'] == 'ok'
        assert len(res['result']) == 2, res
        res = res['result'][0]
        assert 'id' in res, res
        assert 'memberships' in res, res
        assert isinstance(res['memberships'], list), res
        assert 'id' in res['memberships'][0], res
        # from pprint import pprint
        # pprint(res)
        # assert False

    def test_query_simple_filter(self):
        context = get_context()
        q = [{'id': None, 'limit': 10, 'name': 'CSU'}]
        res = context.query(q).results()
        assert res['status'] == 'ok'
        assert len(res['result']) == 1, res
        res0 = res['result'][0]
        assert res0['name'] == 'CSU', res
        assert 'csu' in res0['id'], res

    def test_query_negative_filter(self):
        context = get_context()
        q = [{'id': None, 'limit': 10, 'name!=': 'CSU'}]
        res = context.query(q).results()
        assert res['status'] == 'ok'
        assert len(res['result']) > 1, res
        for rec in res['result']:
            assert rec['name'] != 'CSU', res
            assert 'csu' not in rec['id'], res

    def test_query_regex_filter(self):
        context = get_context()
        q = [{'id': None, 'limit': 10, 'name~=': '90'}]
        res = context.query(q).results()
        assert res['status'] == 'ok'
        assert len(res['result']) == 1, res
        for rec in res['result']:
            assert '90' in rec['name'], rec

    def test_query_list_filter(self):
        context = get_context()
        items = ['SPD', 'CSU']
        q = [{'id': None, 'limit': 10, 'name|=': items}]
        res = context.query(q).results()
        assert res['status'] == 'ok'
        assert len(res['result']) == 2, res
        for rec in res['result']:
            assert rec['name'] in items, rec

    def test_query_negative_list_filter(self):
        context = get_context()
        items = ['SPD', 'CSU']
        q = [{'id': None, 'limit': 1000, 'name|!=': items}]
        res = context.query(q).results()
        assert res['status'] == 'ok'
        assert len(res['result']) > 2, res
        for rec in res['result']:
            assert rec['name'] not in items, rec

    def test_query_wildcard_fields(self):
        context = get_context()
        q = [{'*': None, '$schema': 'persons', 'limit': 10}]
        res = context.query(q).results()
        assert res['status'] == 'ok'
        assert len(res['result']) == 10, res
        for rec in res['result']:
            assert 'id' in rec, rec
            assert 'name' in rec, rec
            assert '$schema' in rec, rec
            assert 'limit' not in rec, rec
            # from pprint import pprint
            # pprint(res)
            # assert False

        q = [{'*': None, 'limit': 10}]
        res = context.query(q).results()
        for rec in res['result']:
            assert '$schema' in rec, rec
            assert 'limit' not in rec, rec
