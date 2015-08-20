# from rdflib import ConjunctiveGraph
from unittest import TestCase

# from jsongraph.metadata import MetaData

from .util import make_test_graph


class MetaDataTestCase(TestCase):

    def setUp(self):
        super(MetaDataTestCase, self).setUp()
        self.graph = make_test_graph()

    def test_basic_context(self):
        data = {'source_url': 'http://pudo.org'}
        ctx = self.graph.context(meta=data)
        assert 'pudo.org' in ctx.meta.get('source_url')
        ctx.meta['label'] = 'Banana'
        assert 'label' in ctx.meta
