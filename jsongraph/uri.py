import os
import yaml
import urllib
import urlparse
import requests


def from_path(path):
    """ Given a file path, make a URI from it. """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return 'file://' + urllib.pathname2url(path)


def to_path(uri):
    if uri.startswith('file://'):
        uri = uri.replace('file://', '')
    return uri


def as_fh(uri):
    """ Get a fileobj for the given URI. """
    scheme = urlparse.urlsplit(uri).scheme.lower()
    if scheme in ['http', 'https']:
        return requests.get(uri)
    return urllib.urlopen(uri)


def as_yaml(uri):
    """ Decode the given URI as YAML (or JSON). """
    return yaml.load(as_fh(uri))


def make_safe(url):
    if url is not None:
        (a, b, c, d, e) = urlparse.urlsplit(url)
        d = urllib.urlencode([(k, v.encode('utf-8'))
                              for (k, v) in urlparse.parse_qsl(d)])
        return urlparse.urlunsplit((a, b, c, d, e)).strip()


def check(text):
    if text is None:
        return False
    text = text.lower()
    return text.startswith('http://') or text.startswith('https://') or \
        text.startswith('urn:') or text.startswith('file://')
