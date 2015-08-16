from uuid import uuid4
from time import time

from rdflib import RDF, Literal
from sparqlquery import Select, v, union, optional, func

from jsongraph.vocab import ID, PRED


class Query(object):
    """ A query against a fully constructed JSON graph. The query language is
    based on Freebase's Metaweb Query Language, a JSON-based query-by-example
    method of interrogating graphs. """

    def __init__(self, context, parent, node):
        self.context = context
        self.parent = parent
        self.node = node
        if node.name is None:
            self.id = 'root'
        else:
            prefix = '_any' if node.name == '*' else node.name
            self.id = '%s_%s' % (prefix, uuid4().hex[:10])
        self.var = v[self.id]

    @property
    def children(self):
        if not hasattr(self, '_children'):
            self._children = []
            for child_node in self.node.children:
                qb = Query(self.context, self, child_node)
                self._children.append(qb)
        return self._children

    @property
    def predicate(self):
        if self.node.name == '$schema':
            return RDF.type
        if self.node.specific_attribute:
            return PRED[self.node.name]
        return v['pred' + self.id]

    def project(self, q):
        """ Figure out which attributes should be returned for the current
        level of the query. """
        attrs = set()
        q = q.project(self.var, append=True)
        for child in self.children:
            if child.node.blank:
                q = child.project(q)
        return q

    def filter(self, q):
        """ Apply any filters to the query. """
        if self.node.leaf and self.node.filtered:
            q = q.where((self.parent.var, self.predicate, Literal(self.node.value)))
        elif self.parent is not None:
            q = q.where((self.parent.var, self.predicate, self.var))
        for child in self.children:
            q = child.filter(q)
        return q

    def query(self):
        """ Compose the query by traversing all nodes and generating SPARQL. """
        q = Select([])
        q = self.project(q)
        q = self.filter(q)

        subq = Select([self.var])
        subq = self.filter(subq)
        if self.parent is None:
            subq = subq.offset(self.node.offset)
            subq = subq.limit(self.node.limit)
        subq = subq.distinct()
        q = q.where(subq)
        print 'QUERY', q.compile()
        return q.execute(self.context.graph)

    def run(self):
        self.query()
        return None

    def results(self):
        t = time()
        result = self.run()
        return {
            'status': 'ok',
            'query': self.node.to_dict(),
            'result': result,
            'time': (time() - t) * 1000
        }
