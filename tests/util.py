import os
import json
import urllib

from jsonschema import RefResolver  # noqa

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
BASE_URI = 'http://www.popoloproject.com/schemas'
PERSON_URI = BASE_URI + '/person.json#'
ORG_URI = BASE_URI + '/organization.json#'
MEM_URI = BASE_URI + '/membership.json#'


def fixture_file(path):
    file_name = os.path.join(fixtures_dir, path)
    return open(file_name, 'rb')


def fixture_uri(path):
    base = os.path.join(fixtures_dir, path)
    base_uri = 'file://' + urllib.pathname2url(base)
    with open(base, 'rb') as fh:
        return json.load(fh), base_uri


def create_resolver():
    resolver = RefResolver(BASE_URI, BASE_URI)
    schemas = os.path.join(fixtures_dir, 'schemas')
    for fn in os.listdir(schemas):
        path = os.path.join(schemas, fn)
        with open(path, 'rb') as fh:
            data = json.load(fh)
            resolver.store[data.get('id')] = data
    return resolver


resolver = create_resolver()


def make_test_graph(buffered=False):
    from jsongraph.graph import Graph
    graph = Graph(resolver=resolver, buffered=buffered)
    graph.register('person', PERSON_URI)
    graph.register('organization', ORG_URI)
    return graph
