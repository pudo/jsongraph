import json
from unittest import TestCase

# from jsongraph.context import load_obj

from .util import make_test_graph, fixture_file


class ContextTestCase(TestCase):

    def setUp(self):
        super(ContextTestCase, self).setUp()
        self.data = json.load(fixture_file('rdfconv/bt_partial.json'))

    def test_basic_load_data(self):
        graph = make_test_graph()
        ctx = graph.context()
        assert 'urn' in repr(ctx), repr(ctx)
        assert str(ctx) in repr(ctx), repr(ctx)
        sc = lambda: len(list(graph.graph.triples((None, None, None))))

        for org in sorted(self.data['organizations']):
            ctx_id = ctx.add('organization', org)
            assert ctx_id is not None
            ctx.delete()
            assert sc() == 0, sc()

    def test_buffered_load_data(self):
        graph = make_test_graph(buffered=True)
        ctx = graph.context()
        assert 'urn' in repr(ctx), repr(ctx)
        assert str(ctx) in repr(ctx), repr(ctx)
        sc = lambda: len(list(graph.graph.triples((None, None, None))))

        for org in sorted(self.data['organizations']):
            ctx_id = ctx.add('organization', org)
            assert ctx_id is not None
            ctx.delete()
            assert sc() == 0, sc()
            break

    def test_restore_context(self):
        graph = make_test_graph()
        ctx = graph.context(prov={'source': 'blah'})
        for org in sorted(self.data['organizations']):
            ctx.add('organization', org)
            break

        ctx.save()
        ctx2 = graph.context(identifier=ctx.identifier)
        assert ctx is not ctx2, (ctx, ctx2)
        assert ctx.prov.data['created_at'] == ctx2.prov.data['created_at'], \
            (ctx.prov.data, ctx2.prov.data)
