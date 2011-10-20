
""" ``collections`` module.
"""

from wheezy.core.comp import defaultdict


class LastItemAdapter(object):
    """ Adapts ``defaultdict(list)``.__getitem__ accessor
        to return a list item from the list. If key is not
        found return None.
    """

    def __init__(self, adaptee):
        """ ``adaptee`` must be defaultdict(list).

            >>> d = defaultdict(list)
            >>> a = last_item_adapter(d)

            Otherwise raise ``TypeError``.

            >>> last_item_adapter(None) # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            TypeError: ...
         """
        if adaptee is None or not(isinstance(adaptee, defaultdict) and
                adaptee.default_factory is list):
            raise TypeError('first argument must be defaultdict(list)')
        self.adaptee = adaptee

    def __getitem__(self, key):
        """
            >>> d = defaultdict(list)
            >>> d['a'].extend([1, 2, 3])
            >>> a = last_item_adapter(d)

            Return a last item from the list.

            >>> a['a']
            3

            If ``key`` not found return ``None``.

            >>> a['x']
        """
        l = self.adaptee[key]
        if l:
            return l[-1]
        return None

last_item_adapter = LastItemAdapter
