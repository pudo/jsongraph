from unittest import TestCase

from jsongraph.query import QueryNode


def query(q):
    qn = QueryNode(None, None, q)
    return qn, qn.to_dict()


class ContextTestCase(TestCase):

    def setUp(self):
        super(ContextTestCase, self).setUp()

    def test_basic_query(self):
        _, res = query({'id': 'foo'})
        assert res['limit'] == 1, res
        assert res['offset'] == 0, res
        assert len(res['children']) == 1, res

    def test_basic_pagination(self):
        _, res = query([{'limit': 10, 'offset': 50}])
        assert res['limit'] == 10, res
        assert res['offset'] == 50, res

        _, res = query({'limit': 10, 'offset': 50})
        assert res['limit'] == 1, res
        assert res['offset'] == 50, res

    def test_nesting(self):
        _, res = query([{'foo': {'bar': 'quux'}, 'xxx': 4}])
        assert len(res['children']) == 2, res['children']

    def test_wildcards(self):
        qn, res = query([{'*': None}])
        assert qn.nested, qn.to_dict()
        for c in qn.children:
            assert not c.specific_attribute, c.to_dict()
            assert not c.nested, c.to_dict()
