
def predicates(graph):
    """ Return a listing of all known predicates in the registered schemata,
    including the schema path they associate with, their name and allowed
    types. """
    seen = set()

    def _traverse(binding):
        if binding.path in seen:
            return
        seen.add(binding.path)

        if binding.is_object:
            for prop in binding.properties:
                yield (binding.path, prop.name, tuple(prop.types))
                for pred in _traverse(prop):
                    yield pred
        elif binding.is_array:
            for item in binding.items:
                for pred in _traverse(item):
                    yield pred

    schemas = graph.aliases.values()
    schemas.extend(graph.resolver.store)
    for schema_uri in graph.aliases.values():
        binding = graph.get_binding(schema_uri, None)
        for pred in _traverse(binding):
            if pred not in seen:
                yield pred
                seen.add(pred)
