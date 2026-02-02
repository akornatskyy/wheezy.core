import unittest
from unittest.mock import Mock

from wheezy.core.pooling import EagerPool, LazyPool, Pooled


class EagerPoolTestCase(unittest.TestCase):
    def test_init(self):
        """Tests if pool fills items per size requested."""
        mock_create_factory = Mock()
        mock_create_factory.return_value = 1
        pool = EagerPool(mock_create_factory, 10)
        assert pool.size == 10
        assert pool.count == 10
        assert 10 == mock_create_factory.call_count

    def test_acquire(self):
        """If an item is aquired it is removed from pool."""
        pool = EagerPool(lambda: 1, 10)

        assert 1 == pool.acquire()
        assert pool.size == 10
        assert pool.count == 9

    def test_get_back(self):
        """An item is returned back to pool."""
        pool = EagerPool(lambda: 1, 10)

        item = pool.acquire()
        pool.get_back(item)

        assert pool.size == 10
        assert pool.count == 10

    def test_fifo(self):
        """Pool items are FIFO cycled."""
        items = [3, 2, 1]

        def create_factory():
            return items.pop()

        pool = EagerPool(create_factory, 3)

        assert 1 == pool.acquire()
        pool.get_back(1)
        assert 2 == pool.acquire()


class LazyPoolTestCase(unittest.TestCase):
    def test_init(self):
        """Tests if pool fills items per size requested."""
        mock_create_factory = Mock()
        mock_create_factory.return_value = 1
        pool = LazyPool(mock_create_factory, 10)
        assert pool.size == 10
        assert pool.count == 10
        assert not mock_create_factory.called

    def test_acquire(self):
        """If an item is aquired it is removed from pool."""
        pool = LazyPool(lambda x: 1, 10)

        assert 1 == pool.acquire()
        assert pool.size == 10
        assert pool.count == 9

    def test_acquire_error(self):
        """If an error has occurred during acquire then get back
        an item to pool and re-raise error.
        """
        mock_create_factory = Mock(side_effect=Exception())
        pool = LazyPool(mock_create_factory, 2)

        self.assertRaises(Exception, pool.acquire)
        assert pool.size == 2
        assert pool.count == 2

    def test_get_back(self):
        """An item is returned back to pool."""
        pool = LazyPool(lambda x: 1, 10)

        item = pool.acquire()
        pool.get_back(item)

        assert pool.size == 10
        assert pool.count == 10

    def test_lifo(self):
        """Pool items are LIFO cycled."""
        items = [3, 2, 1]

        def create_factory(i):
            return i or items.pop()

        pool = LazyPool(create_factory, 3)

        assert 1 == pool.acquire()
        pool.get_back(1)
        assert 1 == pool.acquire()


class PooledTestCase(unittest.TestCase):
    def test_scope(self):
        """Pooled item is available only in the scope of `with` operator."""
        pool = EagerPool(lambda: 1, 10)
        pooled = Pooled(pool)

        item = pooled.__enter__()
        assert 1 == item
        assert pool.count == 9
        pooled.__exit__(None, None, None)
        assert pool.count == 10
        assert pooled.item is None
