from rdflib import RDF


def triplify_object(binding, emit):
    """ Create bi-directional bindings for object relationships. """
    if binding.uri:
        emit((binding.subject, RDF.type, binding.uri))

    if binding.parent is not None:
        parent = binding.parent.subject
        if binding.parent.is_array:
            parent = binding.parent.parent.subject
        emit((parent, binding.predicate, binding.subject))
        if binding.reverse is not None:
            emit((binding.subject, binding.reverse, parent))

    for prop in binding.properties:
        triplify(prop, emit)

    return binding.subject


def triplify(binding, emit):
    """ Recursively generate RDF statement triples from the data and
    schema supplied to the application. """
    if binding.data is None:
        return

    if binding.is_object:
        return triplify_object(binding, emit)
    elif binding.is_array:
        for item in binding.items:
            triplify(item, emit)
    else:
        subject = binding.parent.subject
        emit((subject, binding.predicate, binding.object))
        if binding.reverse is not None:
            emit((binding.object, binding.reverse, subject))
