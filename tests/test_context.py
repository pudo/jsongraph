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
            org_id = ctx.add('organization', org)
            assert org_id is not None

            obj = ctx.get(org_id, schema='organization')
            assert obj['name'] == org['name'], obj
            obj = ctx.get(org_id)
            assert obj['name'] == org['name'], obj
            obj = ctx.get(org_id, schema='foo')
            assert obj is None, obj

            ctx.delete()
            assert sc() == 0, sc()

    def test_read_all(self):
        graph = make_test_graph()
        ctx = graph.context()

        for org in sorted(self.data['organizations']):
            ctx.add('organization', org)

        ctx.save()
        loaded = list(ctx.all('organization'))
        assert len(loaded) == len(self.data['organizations']), loaded
        assert len(loaded) > 0, loaded
        assert 'organization' in loaded[0]['$schema'], loaded[0]

        loaded2 = list(graph.all('organization'))
        assert len(loaded2) == len(self.data['organizations']), loaded2
        assert len(loaded2) > 0, loaded2

        loaded3 = list(graph.all('foo'))
        assert not len(loaded3)

    def test_buffered_load_data(self):
        graph = make_test_graph(buffered=True)
        ctx = graph.context()
        assert 'urn' in repr(ctx), repr(ctx)
        assert str(ctx) in repr(ctx), repr(ctx)
        sc = lambda: len(list(graph.graph.triples((None, None, None))))

        for org in sorted(self.data['organizations']):
            org_id = ctx.add('organization', org)
            assert org_id is not None
            assert sc() == 0, sc()
            ctx.save()
            assert sc() != 0, sc()
            ctx.delete()
            assert sc() == 0, sc()
            break

    def test_restore_context(self):
        graph = make_test_graph()
        ctx = graph.context(meta={'source': 'blah'})
        for org in sorted(self.data['organizations']):
            ctx.add('organization', org)
            break

        ctx.save()
        ctx2 = graph.context(identifier=ctx.identifier)
        assert ctx is not ctx2, (ctx, ctx2)
        assert ctx.meta.data['created_at'] == ctx2.meta.data['created_at'], \
            (ctx.meta.data, ctx2.meta.data)
