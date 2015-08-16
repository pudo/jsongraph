from unittest import TestCase

from jsongraph.query import QueryNode, util


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

    def test_inverted(self):
        qn, res = query([{'!foo': 'tmux'}])
        for c in qn.children:
            assert c.inverted, (c, c.inverted)

    def test_operators(self):
        qn, res = query([{
            'foo': 5,
            'bar~=': "hello",
            "x!=": "lala",
            "t|=": [4, 5]
        }])
        assert len(res['children']) == 4, res['children']
        for c in qn.children:
            if c.name == 'foo':
                assert c.op == util.OP_EQ
            elif c.name == 'bar':
                assert c.op == util.OP_LIKE
            elif c.name == 'x':
                assert c.op == util.OP_NOT
            elif c.name == 't':
                assert c.op == util.OP_IN
            else:
                assert False, (c, c.name)

    def test_wildcards(self):
        qn, res = query([{'*': None}])
        assert qn.nested, qn.to_dict()
        for c in qn.children:
            assert not c.specific_attribute, c.to_dict()
            assert not c.nested, c.to_dict()
