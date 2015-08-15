import json
from unittest import TestCase

# from jsongraph.context import load_obj

from .util import make_test_graph, fixture_file


class ContextTestCase(TestCase):

    def setUp(self):
        super(ContextTestCase, self).setUp()
        self.data = json.load(fixture_file('rdfconv/bt_partial.json'))
        self.graph = make_test_graph()

    def test_basic_load_data(self):
        ctx = self.graph.context()
        assert 'urn' in repr(ctx), repr(ctx)
        assert str(ctx) in repr(ctx), repr(ctx)

        for org in sorted(self.data['organizations']):
            ctx_id = ctx.add('organization', org)
            assert ctx_id is not None
            break

        # for pers in self.data['persons']:
        #     ctx_id = ctx.add('person', pers)
        #     assert ctx_id is not None
        #     break

        sc = lambda: len(list(self.graph.graph.triples((None, None, None))))
        ctx_len = len(list(ctx.graph.triples((None, None, None))))
        assert sc() == 0, sc()
        assert ctx_len != 0, ctx_len
        ctx.save()
        assert sc() == ctx_len, sc()
        ctx.delete()
        assert sc() == 0, sc()
