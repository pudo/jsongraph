import json
import copy
from nose.tools import raises
from unittest import TestCase

from jsongraph.util import GraphException

from .util import make_test_graph, fixture_file

DATA = json.load(fixture_file('rdfconv/bt_partial.json'))


class ContextTestCase(TestCase):

    def setUp(self):
        super(ContextTestCase, self).setUp()
        self.data = copy.deepcopy(DATA)

    def test_basic_load_data(self):
        graph = make_test_graph()
        ctx = graph.context()
        assert 'urn' in repr(ctx), repr(ctx)
        assert str(ctx) in repr(ctx), repr(ctx)
        sc = lambda: len(list(graph.graph.triples((None, None, None))))

        for org in sorted(self.data['organizations']):
            org_id = ctx.add('organizations', org)
            assert org_id is not None

            obj = ctx.get(org_id, schema='organizations')
            assert obj['name'] == org['name'], obj
            obj = ctx.get(org_id)
            assert obj['name'] == org['name'], obj

            ctx.delete()
            assert sc() == 0, sc()

    @raises(GraphException)
    def test_basic_get_invalid_schema(self):
        graph = make_test_graph()
        ctx = graph.context()
        for org in sorted(self.data['organizations']):
            uri = ctx.add('organizations', org)
            ctx.get(uri, schema='foo')

    def test_read_all(self):
        graph = make_test_graph()
        ctx = graph.context()

        for org in sorted(self.data['organizations']):
            ctx.add('organizations', org)

        ctx.save()
        loaded = list(ctx.all('organizations'))
        assert len(loaded) == len(self.data['organizations']), loaded
        assert len(loaded) > 0, loaded
        assert 'organization' in loaded[0]['$schema'], loaded[0]

        loaded2 = list(graph.all('organizations'))
        assert len(loaded2) == len(self.data['organizations']), loaded2
        assert len(loaded2) > 0, loaded2

    @raises(GraphException)
    def test_basic_all_invalid_schema(self):
        graph = make_test_graph()
        list(graph.all('foo'))

    def test_buffered_load_data(self):
        graph = make_test_graph(buffered=True)
        ctx = graph.context()
        assert 'urn' in repr(ctx), repr(ctx)
        assert str(ctx) in repr(ctx), repr(ctx)
        sc = lambda: len(list(graph.graph.triples((None, None, None))))

        for org in sorted(self.data['organizations']):
            org_id = ctx.add('organizations', org)
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
            ctx.add('organizations', org)
            break

        ctx.save()
        ctx2 = graph.context(identifier=ctx.identifier)
        assert ctx is not ctx2, (ctx, ctx2)
        assert ctx.meta['created_at'] == ctx2.meta['created_at'], \
            (ctx.meta, ctx2.meta)

    def test_delete_all_data(self):
        graph = make_test_graph()
        ctx = graph.context(meta={'source': 'blah'})
        for org in sorted(self.data['organizations']):
            ctx.add('organizations', org)
            break
        sc = lambda: len(list(graph.graph.triples((None, None, None))))
        assert sc() != 0, sc()
        graph.clear(context='foo')
        assert sc() != 0, sc()
        graph.clear()
        assert sc() == 0, sc()
