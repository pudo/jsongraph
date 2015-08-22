# from rdflib import ConjunctiveGraph
from unittest import TestCase

from jsongraph import reflect

from .util import make_test_graph, ORG_URI


class ReflectTestCase(TestCase):

    def setUp(self):
        super(ReflectTestCase, self).setUp()
        self.graph = make_test_graph()

    def test_predicates(self):
        preds = list(reflect.predicates(self.graph))
        t = ('string', 'null')
        assert (ORG_URI, 'name', t) in preds, preds
        t = ('array',)
        assert (ORG_URI, 'memberships', t) in preds, preds
