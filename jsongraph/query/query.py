

class Query(object):
    """ A query against a fully constructed JSON graph. The query language is
    based on Freebase's Metaweb Query Language, a JSON-based query-by-example
    method of interrogating graphs. """

    def __init__(self, context, parent, node):
        self.context = context
        self.parent = parent
        self.node = node

    def query(self):
        return None
