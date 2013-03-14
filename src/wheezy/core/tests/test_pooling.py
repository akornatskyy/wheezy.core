
""" Unit tests for ``wheezy.core.pooling``.
"""

import unittest

from mock import Mock


class EagerPoolTestCase(unittest.TestCase):

    def test_init(self):
        """ Tests if pool fills items per size requested.
        """
        from wheezy.core.pooling import EagerPool
        mock_create_factory = Mock()
        mock_create_factory.return_value = 1
        pool = EagerPool(mock_create_factory, 10)
        assert pool.size == 10
        assert pool.count == 10
        assert 10 == mock_create_factory.call_count

    def test_acquire(self):
        """ If an item is aquired it is removed from pool.
        """
        from wheezy.core.pooling import EagerPool
        pool = EagerPool(lambda: 1, 10)

        assert 1 == pool.acquire()
        assert pool.size == 10
        assert pool.count == 9

    def test_get_back(self):
        """ An item is returned back to pool.
        """
        from wheezy.core.pooling import EagerPool
        pool = EagerPool(lambda: 1, 10)

        item = pool.acquire()
        pool.get_back(item)

        assert pool.size == 10
        assert pool.count == 10

    def test_fifo(self):
        """ Pool items are FIFO cycled.
        """
        from wheezy.core.pooling import EagerPool
        items = [3, 2, 1]

        def create_factory():
            return items.pop()
        pool = EagerPool(create_factory, 3)

        assert 1 == pool.acquire()
        pool.get_back(1)
        assert 2 == pool.acquire()


class LazyPoolTestCase(unittest.TestCase):

    def test_init(self):
        """ Tests if pool fills items per size requested.
        """
        from wheezy.core.pooling import LazyPool
        mock_create_factory = Mock()
        mock_create_factory.return_value = 1
        pool = LazyPool(mock_create_factory, 10)
        assert pool.size == 10
        assert pool.count == 10
        assert not mock_create_factory.called

    def test_acquire(self):
        """ If an item is aquired it is removed from pool.
        """
        from wheezy.core.pooling import LazyPool
        pool = LazyPool(lambda x: 1, 10)

        assert 1 == pool.acquire()
        assert pool.size == 10
        assert pool.count == 9

    def test_get_back(self):
        """ An item is returned back to pool.
        """
        from wheezy.core.pooling import LazyPool
        pool = LazyPool(lambda x: 1, 10)

        item = pool.acquire()
        pool.get_back(item)

        assert pool.size == 10
        assert pool.count == 10

    def test_lifo(self):
        """ Pool items are LIFO cycled.
        """
        from wheezy.core.pooling import LazyPool
        items = [3, 2, 1]

        def create_factory(i):
            return i or items.pop()
        pool = LazyPool(create_factory, 3)

        assert 1 == pool.acquire()
        pool.get_back(1)
        assert 1 == pool.acquire()


class PooledTestCase(unittest.TestCase):

    def test_scope(self):
        """ Pooled item is available only in the scope of `with` operator.
        """
        from wheezy.core.pooling import EagerPool
        from wheezy.core.pooling import Pooled
        pool = EagerPool(lambda: 1, 10)
        pooled = Pooled(pool)

        item = pooled.__enter__()
        assert 1 == item
        assert pool.count == 9
        pooled.__exit__(None, None, None)
        assert pool.count == 10
        assert pooled.item is None
