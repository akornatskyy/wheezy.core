
""" ``comp`` module.
"""

import sys


PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2
PY3 = PY_MAJOR >= 3

if PY2 and PY_MINOR == 4:  # pragma: nocover
    __import__ = __import__
else:  # pragma: nocover
    # perform absolute import
    __saved_import__ = __import__
    __import__ = lambda n, g=None, l=None, f=None:\
            __saved_import__(n, g, l, f, 0)


try:  # pragma: nocover
    from collections import defaultdict
except ImportError:  # pragma: nocover

    class defaultdict(dict):

        def __init__(self, default_factory=None, *args, **kwargs):
            if default_factory and \
                not hasattr(default_factory, '__call__'):
                raise TypeError('first argument must be callable')
            dict.__init__(self, *args, **kwargs)
            self.default_factory = default_factory

        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)

        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value

        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.items()

        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))