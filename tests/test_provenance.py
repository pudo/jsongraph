# from rdflib import ConjunctiveGraph
from unittest import TestCase

from jsongraph.provenance import Provenance

from .util import make_test_graph


class ProvenanceTestCase(TestCase):

    def setUp(self):
        super(ProvenanceTestCase, self).setUp()
        self.graph = make_test_graph()

    def test_basic_context(self):
        data = {'source_url': 'http://pudo.org'}
        ctx = self.graph.context(prov=data)
        assert 'pudo.org' in ctx.prov.data.get('source_url')
