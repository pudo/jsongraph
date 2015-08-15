from jsonschema import RefResolver


class Graph(object):
    """ Registry for assigning names aliases to certain schemata. """

    def __init__(self, base_uri=None, resolver=None, aliases=None):
        self._resolver = resolver
        self._base_uri = base_uri
        self.aliases = aliases or {}

    @property
    def base_uri(self):
        if self._base_uri is None:
            if self._resolver is not None:
                return self.resolver.resolution_scope
        return self._base_uri

    @property
    def resolver(self):
        if self._resolver is None:
            self._resolver = RefResolver(self.base_uri, {})
        return self._resolver

    def register(self, alias, uri):
        """ Register a new schema URI under a given name. """
        # TODO: do we want to constrain the valid alias names.
        self.aliases[alias] = uri

    @property
    def names(self):
        return self.aliases.keys()

    def get_uri(self, alias):
        """ Get the URI for a given alias. A registered URI will return itself,
        otherwise ``None`` is returned. """
        if alias in self.aliases.keys():
            return self.aliases[alias]
        if alias in self.aliases.values():
            return alias

    def get_schema(self, alias):
        """ Actually resolve the schema for the given alias/URI. """
        uri = self.get_uri(alias)
        uri, schema = self.resolver.resolve(uri)
        return schema
