
""" Unit tests for ``wheezy.core.retry``.
"""

import unittest

from mock import Mock
from mock import call
from mock import patch


class RetryTestCase(unittest.TestCase):

    def setUp(self):
        self.time_patcher = patch('wheezy.core.retry.time')
        self.mock_time = self.time_patcher.start()
        self.sleep_patcher = patch('wheezy.core.retry.sleep')
        self.mock_sleep = self.sleep_patcher.start()

    def tearDown(self):
        self.time_patcher.stop()
        self.sleep_patcher.stop()

    def test_asserts(self):
        """ Ensure arguments asserts
        """
        from wheezy.core.retry import make_retry
        # timeout > 0.0
        self.assertRaises(
            AssertionError,
            lambda: make_retry(timeout=0, min_delay=0, slope=0,
                               delta=0, max_delay=0))
        # min_delay > 0.0
        self.assertRaises(
            AssertionError,
            lambda: make_retry(timeout=10, min_delay=0, slope=0,
                               delta=0, max_delay=0))
        # max_delay > 0.0
        self.assertRaises(
            AssertionError,
            lambda: make_retry(timeout=10, min_delay=1, slope=0,
                               delta=0, max_delay=0))
        # timeout > min_delay
        self.assertRaises(
            AssertionError,
            lambda: make_retry(timeout=1, min_delay=2, slope=0,
                               delta=0, max_delay=0))
        # timeout > max_delay
        self.assertRaises(
            AssertionError,
            lambda: make_retry(timeout=10, min_delay=1, slope=0,
                               delta=0, max_delay=11))

    def test_immediately(self):
        """ Ensure first succeed attempt does not require calls to
            time and sleep.
        """
        from wheezy.core.retry import make_retry
        retry = make_retry(timeout=10, min_delay=1, slope=0, delta=0,
                           max_delay=2)
        assert retry(lambda: True)
        assert not self.mock_time.called
        assert not self.mock_sleep.called

    def test_slope(self):
        """ Ensure sleep sequence when slope argument is used.
        """
        from wheezy.core.retry import make_retry
        retry = make_retry(timeout=10.0, min_delay=0.5, slope=2.0, delta=0.0,
                           max_delay=2.5)
        self.mock_time.return_value = 0.0
        mock_acquire = Mock(side_effect=[False, False, False, False, True])
        assert retry(mock_acquire)
        assert 4 == self.mock_time.call_count
        assert [call(0.5), call(1.0), call(2.0), call(2.5)
                ] == self.mock_sleep.call_args_list

    def test_delta(self):
        """ Ensure sleep sequence when delta argument is used.
        """
        from wheezy.core.retry import make_retry
        retry = make_retry(timeout=10.0, min_delay=0.5, slope=1.0, delta=0.5,
                           max_delay=2.0)
        self.mock_time.return_value = 0.0
        mock_acquire = Mock(side_effect=[False, False, False, False, True])
        assert retry(mock_acquire)
        assert 4 == self.mock_time.call_count
        assert [call(0.5), call(1.0), call(1.5), call(2.0)
                ] == self.mock_sleep.call_args_list

    def test_remains_skip(self):
        """ Ensure the function returns immediately when there is no
            remaining time left.
        """
        from wheezy.core.retry import make_retry
        retry = make_retry(timeout=10.0, min_delay=0.5, slope=2.0, delta=0.0,
                           max_delay=2.5)
        self.mock_time.side_effect = [0.0, 10.25]
        assert not retry(lambda: False)
        assert 2 == self.mock_time.call_count
        assert [call(0.5)] == self.mock_sleep.call_args_list

    def test_remains_timeout(self):
        """ Ensure the function sleeps for remaining time left.
        """
        from wheezy.core.retry import make_retry
        retry = make_retry(timeout=10.0, min_delay=0.5, slope=2.0, delta=0.0,
                           max_delay=2.5)
        self.mock_time.side_effect = [0.0, 1.0, 9.25]
        assert not retry(lambda: False)
        assert 3 == self.mock_time.call_count
        assert [call(0.5), call(1.0), call(0.75)
                ] == self.mock_sleep.call_args_list
