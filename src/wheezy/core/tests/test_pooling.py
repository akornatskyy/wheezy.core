
""" Unit tests for ``wheezy.core.pooling``.
"""

import unittest


class EagerPoolTestCase(unittest.TestCase):

    def test_init(self):
        """
        """
        from wheezy.core.pooling import EagerPool
        pool = EagerPool(lambda: 1, 10)
        assert pool.size == 10
        assert pool.count == 10

    def test_acquire(self):
        from wheezy.core.pooling import EagerPool
        pool = EagerPool(lambda: 1, 10)

        assert 1 == pool.acquire()
        assert pool.size == 10
        assert pool.count == 9

    def test_get_back(self):
        from wheezy.core.pooling import EagerPool
        pool = EagerPool(lambda: 1, 10)

        item = pool.acquire()
        pool.get_back(item)

        assert pool.size == 10
        assert pool.count == 10


class PooledTestCase(unittest.TestCase):

    def test_scope(self):
        from wheezy.core.pooling import EagerPool
        from wheezy.core.pooling import Pooled
        pool = EagerPool(lambda: 1, 10)
        pooled = Pooled(pool)

        item = pooled.__enter__()
        assert 1 == item
        assert pool.count == 9
        pooled.__exit__(None, None, None)
        assert pool.count == 10
