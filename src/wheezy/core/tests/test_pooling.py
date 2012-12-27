
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
