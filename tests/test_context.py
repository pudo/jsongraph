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
        sc = lambda: len(list(self.graph.graph.triples((None, None, None))))

        for org in sorted(self.data['organizations']):
            ctx_id = ctx.add('organization', org)
            assert ctx_id is not None
            ctx.delete()
            assert sc() == 0, sc()
            break

    def test_restore_context(self):
        ctx = self.graph.context()
        for org in sorted(self.data['organizations']):
            ctx.add('organization', org)
            break

        ctx2 = self.graph.context(identifier=ctx.identifier)
        assert ctx is not ctx2, (ctx, ctx2)
        assert ctx.prov.data['created_at'] == ctx2.prov.data['created_at']
