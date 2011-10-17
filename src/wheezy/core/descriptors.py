
""" ``descriptors`` module.
"""

class attribute(object):
    """ ``attribute`` decorator is intended to promote a
        function call to object attribute. This means the
        function is called once and replaced with
        returned value.

        >>> class A:
        ...     def __init__(self):
        ...         self.counter = 0
        ...     @attribute
        ...     def count(self):
        ...         self.counter += 1
        ...         return self.counter
        >>> a = A()
        >>> a.count
        1
        >>> a.count
        1
    """
    def __init__(self, f):
        self.f = f
        self.__module__ = f.__module__
        self.__name__ = f.__name__
        self.__doc__ = f.__doc__

    def __get__(self, obj, t=None):
        val = self.f(obj)
        setattr(obj, self.f.__name__, val)
        return val
