from datetime import datetime

from rdflib import Literal
from rdflib.namespace import RDF

from jsongraph.vocab import META


class Provenance(object):
    """ This object retains information on the origin and trustworthiness of
    a particular subset of the data. """

    def __init__(self, context, data=None):
        self.context = context
        self.data = self._load()
        self.data.update(data or {})
        if 'created_at' not in self.data:
            self.data['created_at'] = datetime.utcnow()
        self.saved = False

    def _load(self):
        """ Load provenance info from the main store. """
        data, graph = {}, self.context.parent.graph
        for (_, p, o) in graph.triples((self.context.identifier, None, None)):
            if not p.startswith(META):
                continue
            name = p[len(META):]
            data[name] = o.toPython()
        return data

    def generate(self):
        """ Add provenance info to the context graph. """
        t = (self.context.identifier, RDF.type, META.Provenance)
        if t not in self.context.graph:
            self.context.graph.add(t)
        for name, value in self.data.items():
            t = (self.context.identifier, META[name], Literal(value))
            if t not in self.context.graph:
                self.context.graph.add(t)
