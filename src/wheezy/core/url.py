""" ``url`` module
"""

from wheezy.core.comp import urlunsplit


def urlparts(parts=None, scheme=None, netloc=None, path=None,
        query=None, fragment=None):
    """ ``parts`` must be a 5-tuple:
        (scheme, netloc, path, query, fragment)

        >>> from wheezy.core.comp import urlsplit
        >>> parts = urlsplit('http://www.python.org/dev/peps/pep-3333')
        >>> urlparts(parts)
        urlparts('http', 'www.python.org', '/dev/peps/pep-3333', '', '')
        >>> urlparts(scheme='https', path='/test')
        urlparts('https', None, '/test', None, None)

        Otherwise raise assertion error

        >>> urlparts(('https', )) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        AssertionError: ...
    """
    if not parts:
        parts = (scheme, netloc, path, query, fragment)
    return UrlParts(parts)


class UrlParts(tuple):

    def __init__(self, parts):
        assert len(parts) == 5, '`parts` must be a tupple of length 6'
        super(UrlParts, self).__init__()

    def __repr__(self):
        return 'urlparts' + super(UrlParts, self).__repr__()

    def geturl(self):
        """
            >>> from wheezy.core.comp import urlsplit
            >>> parts = urlsplit('http://www.python.org/dev/peps/pep-3333')
            >>> parts = urlparts(parts)
            >>> parts.geturl()
            'http://www.python.org/dev/peps/pep-3333'
        """
        return urlunsplit(self)

    def join(self, other):
        """
            >>> from wheezy.core.comp import urlsplit
            >>> parts = urlsplit('http://www.python.org/dev/peps/pep-3333')
            >>> parts = urlparts(parts)
            >>> parts = parts.join(urlparts(scheme='https', path='/test'))
            >>> parts.geturl()
            'https://www.python.org/test'
        """
        parts = (
                other[0] or self[0],
                other[1] or self[1],
                other[2] or self[2],
                other[3] or self[3],
                other[4] or self[4])
        return UrlParts(parts)
