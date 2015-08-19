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
        self._results = []
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
        q = q.project(self.var, append=True)
        for child in self.children:
            if child.node.blank and child.node.leaf:
                q = child.project(q)
        return q

    def filter(self, q):
        """ Apply any filters to the query. """
        if self.node.leaf and self.node.filtered:
            q = q.where((self.parent.var,
                         self.predicate,
                         Literal(self.node.value)))
        elif self.parent is not None:
            q = q.where((self.parent.var, self.predicate, self.var))
        for child in self.children:
            q = child.filter(q)
        return q

    def query(self):
        """ Compose the query and generate SPARQL. """
        q = Select([])
        q = self.project(q)
        q = self.filter(q)

        if self.parent is None:
            subq = Select([self.var])
            subq = self.filter(subq)
            subq = subq.offset(self.node.offset)
            subq = subq.limit(self.node.limit)
            subq = subq.distinct()
            q = q.where(subq)

        print 'QUERY', q.compile()
        return q

    def collect(self, row):
        parent = None
        if self.parent:
            parent = row.get(self.parent.id)

        name = self.node.name
        value = row.get(self.id)
        self._results.append((parent, name, value))

        for child in self.children:
            child.collect(row)

    def assemble(self, parent_id=None):
        items = []
        name = None
        for (parent, name, value) in self._results:
            if parent != parent_id:
                continue

            if self.node.leaf:
                items.append(value)
            else:
                data = {}
                for child in self.children:
                    name, out = child.assemble(parent_id=value)
                    data[name] = out
                items.append(data)

        if not self.node.many:
            items = items.pop() if len(items) else None
        return name, items

    def run(self):
        res = self.query().execute(self.context.graph)
        for row in res:
            data = {}
            for k, val in row.asdict().items():
                data[k] = val.toPython()
            self.collect(data)
        name, result = self.assemble()
        return result

    def results(self):
        t = time()
        result = self.run()
        return {
            'status': 'ok',
            'query': self.node.to_dict(),
            'result': result,
            'time': (time() - t) * 1000
        }
