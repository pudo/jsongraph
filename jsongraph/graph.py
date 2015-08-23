import logging

from rdflib import URIRef, plugin, ConjunctiveGraph
from rdflib.store import Store
from rdflib.plugins.memory import Memory, IOMemory
from jsonschema import RefResolver, ValidationError

from jsongraph.context import Context
from jsongraph.config import config_validator
from jsongraph.common import GraphOperations
from jsongraph.util import sparql_store, GraphException

log = logging.getLogger(__name__)


class Graph(GraphOperations):
    """ Registry for assigning names aliases to certain schemata. """

    def __init__(self, base_uri=None, resolver=None, config=None):
        self.config = config or {}
        try:
            config_validator.validate(self.config)
        except ValidationError as ve:
            raise GraphException("Invalid config: %r" % ve)
        self._resolver = resolver
        self._base_uri = base_uri
        self._store = None
        self._buffered = None
        self.aliases = {}
        for alias, schema in self.config.get('schemas', {}).items():
            self.register(alias, schema)

    @property
    def parent(self):
        return self

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
        # if self.base_uri not in self._resolver.store:
        #    self._resolver.store[self.base_uri] = self.config
        return self._resolver

    @property
    def store(self):
        """ Backend storage for RDF data. Either an in-memory store, or an
        external triple store controlled via SPARQL. """
        if self._store is None:
            config = self.config.get('store', {})
            if 'query' in config and 'update' in config:
                self._store = sparql_store(config.get('query'),
                                           config.get('update'))
            else:
                self._store = plugin.get('IOMemory', Store)()
            log.debug('Created store: %r', self._store)
        return self._store

    @property
    def graph(self):
        """ A conjunctive graph of all statements in the current instance. """
        if not hasattr(self, '_graph') or self._graph is None:
            self._graph = ConjunctiveGraph(store=self.store,
                                           identifier=self.base_uri)
        return self._graph

    @property
    def buffered(self):
        """ Whether write operations should be buffered, i.e. run against a
        local graph before being stored to the main data store. """
        if 'buffered' not in self.config:
            return not isinstance(self.store, (Memory, IOMemory))
        return self.config.get('buffered')

    def context(self, identifier=None, meta=None):
        """ Get or create a context, with the given identifier and/or
        provenance meta data. A context can be used to add, update or delete
        objects in the store. """
        return Context(self, identifier=identifier, meta=meta)

    def register(self, alias, uri):
        """ Register a new schema URI under a given name. """
        # TODO: do we want to constrain the valid alias names.
        if isinstance(uri, dict):
            id = uri.get('id', alias)
            self.resolver.store[id] = uri
            uri = id
        self.aliases[alias] = uri

    def get_uri(self, alias):
        """ Get the URI for a given alias. A registered URI will return itself,
        otherwise ``None`` is returned. """
        if alias in self.aliases.keys():
            return self.aliases[alias]
        if alias in self.aliases.values():
            return alias
        raise GraphException('No such schema: %r' % alias)

    def get_schema(self, alias):
        """ Actually resolve the schema for the given alias/URI. """
        if isinstance(alias, dict):
            return alias
        uri = self.get_uri(alias)
        if uri is None:
            raise GraphException('No such schema: %r' % alias)
        uri, schema = self.resolver.resolve(uri)
        return schema

    def clear(self, context=None):
        """ Delete all data from the graph. """
        context = URIRef(context).n3() if context is not None else '?g'
        query = """
            DELETE { GRAPH %s { ?s ?p ?o } } WHERE { GRAPH %s { ?s ?p ?o } }
        """ % (context, context)
        self.parent.graph.update(query)

    def __str__(self):
        return self.base_uri

    def __repr__(self):
        return '<Graph("%s")>' % self.base_uri
