import urllib
import urlparse


def to_path(uri):
    if uri.startswith('file://'):
        uri = uri.replace('file://', '')
    return uri


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
