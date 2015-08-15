

class SchemaRegistry(object):
    """ Registry for assigning names aliases to certain schemata. """

    def __init__(self, resolver, aliases=None):
        self.resolver = resolver
        self.aliases = aliases or {}

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
