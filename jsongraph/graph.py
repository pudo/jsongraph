from rdflib import URIRef, plugin, ConjunctiveGraph
from rdflib.store import Store
from jsonschema import RefResolver

from jsongraph.context import Context


class Graph(object):
    """ Registry for assigning names aliases to certain schemata. """

    def __init__(self, base_uri=None, resolver=None, aliases=None,
                 rdf_store=None):
        self._resolver = resolver
        self._base_uri = base_uri
        self._store = rdf_store
        self.aliases = aliases or {}

    @property
    def base_uri(self):
        """ Resolution base for JSON schema. Also used as the default
        graph ID for RDF. """
        if self._base_uri is None:
            if self._resolver is not None:
                self._base_uri = self.resolver.resolution_scope
            else:
                self._base_uri = 'http://pudo.github.io/jsongraph'
        return URIRef(self._base_uri)

    @property
    def resolver(self):
        """ Resolver for JSON Schema references. This can be based around a
        file or HTTP-based resolution base URI. """
        if self._resolver is None:
            self._resolver = RefResolver(self.base_uri, {})
        return self._resolver

    @property
    def store(self):
        """ Backend storage for RDF data. Either an in-memory store, or an
        external triple store controlled via SPARQL. """
        if self._store is None:
            self._store = plugin.get('IOMemory', Store)()
        return self._store

    @property
    def graph(self):
        """ A conjunctive graph of all statements in the current instance. """
        if not hasattr(self, '_graph') or self._graph is None:
            self._graph = ConjunctiveGraph(store=self.store,
                                           identifier=self.base_uri)
        return self._graph

    def context(self, identifier=None, provenance=None):
        """ Get or create a context, with the given identifier and/or
        provenance data. A context can be used to add, update or delete
        objects in the store. """
        return Context(self, identifier=identifier, provenance=provenance)

    def register(self, alias, uri):
        """ Register a new schema URI under a given name. """
        # TODO: do we want to constrain the valid alias names.
        self.aliases[alias] = uri

    def get_uri(self, alias):
        """ Get the URI for a given alias. A registered URI will return itself,
        otherwise ``None`` is returned. """
        if alias in self.aliases.keys():
            return self.aliases[alias]
        if alias in self.aliases.values():
            return alias

    def get_schema(self, alias):
        """ Actually resolve the schema for the given alias/URI. """
        if isinstance(alias, dict):
            return alias
        uri = self.get_uri(alias)
        if uri is None:
            return None
        uri, schema = self.resolver.resolve(uri)
        return schema

    def __str__(self):
        return self.base_uri

    def __repr__(self):
        return '<Graph("%s")>' % self.base_uri
