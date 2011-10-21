
""" ``collections`` module.
"""

from wheezy.core.comp import defaultdict


def first_item_adapter(adaptee):
    """ Adapts ``defaultdict(list)``.__getitem__ accessor to
        return the first item from the list.

        >>> d = defaultdict(list)
        >>> d['a'].extend([1, 2, 3])
        >>> a = first_item_adapter(d)

        Return a first item from the list.

        >>> a['a']
        1
    """
    return ItemAdapter(adaptee, 0)


def last_item_adapter(adaptee):
    """ Adapts ``defaultdict(list)``.__getitem__ accessor to
        return the last item from the list.

        >>> d = defaultdict(list)
        >>> d['a'].extend([1, 2, 3])
        >>> a = last_item_adapter(d)

        Return a last item from the list.

        >>> a['a']
        3
    """
    return ItemAdapter(adaptee, -1)


class ItemAdapter(object):
    """ Adapts ``defaultdict(list)``.__getitem__ accessor to
        return item at ``index`` from the list. If ``key`` is not
        found return None.
    """

    def __init__(self, adaptee, index):
        """ ``adaptee`` must be defaultdict(list).

            >>> d = defaultdict(list)
            >>> a = ItemAdapter(d, 0)

            Otherwise raise ``TypeError``.

            >>> ItemAdapter(None, 0) # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            TypeError: ...
         """
        if adaptee is None or not isinstance(adaptee, dict):
            raise TypeError('first argument must be defaultdict(list)')
        self.adaptee = adaptee
        self.index = index

    def __getitem__(self, key):
        """
            >>> d = defaultdict(list)
            >>> d['a'].extend([1, 2, 3])
            >>> a = ItemAdapter(d, 0)

            Return a first item from the list.

            >>> a['a']
            1

            >>> a = ItemAdapter(d, -1)

            Return a last item from the list.

            >>> a['a']
            3

            If ``key`` not found return ``None``.

            >>> a['x']
        """
        l = self.adaptee[key]
        if l:
            return l[self.index]
        return None
