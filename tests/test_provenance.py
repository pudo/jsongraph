# from rdflib import ConjunctiveGraph
from unittest import TestCase

from jsongraph import provenance


class ProvenanceTestCase(TestCase):

    def setUp(self):
        super(ProvenanceTestCase, self).setUp()

    def test_basic_context(self):
        ctx = provenance.get_context(source_url='http://pudo.org')
        assert len(ctx) == 3, len(ctx)
        assert 'pudo.org' in ctx.identifier, ctx.identifier

    def test_title(self):
        ctx = provenance.get_context(source_url='http://pudo.org',
                                     source_title='Foo Bar')
        assert len(ctx) == 4, len(ctx)

    def test_file(self):
        ctx = provenance.get_context(source_file='README.txt')
        assert len(ctx) == 3, len(ctx)
        assert 'file://README.txt' in ctx.identifier, ctx.identifier
        # assert False, ctx.serialize(format='n3')
