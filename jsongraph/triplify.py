from rdflib import RDF


def triplify_object(binding):
    """ Create bi-directional bindings for object relationships. """
    triples = []
    if binding.uri:
        triples.append((binding.subject, RDF.type, binding.uri))

    if binding.parent is not None:
        parent = binding.parent.subject
        if binding.parent.is_array:
            parent = binding.parent.parent.subject
        triples.append((parent, binding.predicate, binding.subject))
        if binding.reverse is not None:
            triples.append((binding.subject, binding.reverse, parent))

    for prop in binding.properties:
        _, prop_triples = triplify(prop)
        triples.extend(prop_triples)

    return binding.subject, triples


def triplify(binding):
    """ Recursively generate RDF statement triples from the data and
    schema supplied to the application. """
    triples = []
    if binding.data is None:
        return None, triples

    if binding.is_object:
        return triplify_object(binding)
    elif binding.is_array:
        for item in binding.items:
            _, item_triples = triplify(item)
            triples.extend(item_triples)
        return None, triples
    else:
        subject = binding.parent.subject
        triples.append((subject, binding.predicate, binding.object))
        if binding.reverse is not None:
            triples.append((binding.object, binding.reverse, subject))
        return subject, triples
