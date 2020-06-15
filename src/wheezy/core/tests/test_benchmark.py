""" Unit tests for ``wheezy.core.benchmark``.
"""

import unittest

from mock import Mock


class BenchmarkTestCase(unittest.TestCase):
    def test_run(self):
        """ Ensure targets are called.
        """
        from wheezy.core.benchmark import Benchmark

        t1 = Mock()
        t1.__name__ = "t1"
        t2 = Mock()
        t2.__name__ = "t2"
        b = Benchmark((t1, t2), 20)
        r = list(b.run())
        assert 2 == len(r)
        name, timing = r[0]
        assert "t1" == name
        assert timing >= 0
        name, timing = r[1]
        assert "t2" == name
        assert timing >= 0
        assert 30 == t1.call_count
        assert 30 == t2.call_count

    def test_run_timer(self):
        """ Ensure timer is used.
        """
        from mock import PropertyMock

        from wheezy.core.benchmark import Benchmark

        t1 = Mock()
        t1.__name__ = "t1"
        mock_timer = Mock()
        mock_timing = PropertyMock(return_value=5)
        type(mock_timer).timing = mock_timing
        b = Benchmark((t1,), 20, timer=mock_timer)
        name, timing = list(b.run())[0]
        assert "t1" == name
        assert 5 == timing
        mock_timer.start.assert_called_with()
        assert 2 == mock_timer.start.call_count
        mock_timer.stop.assert_called_with()
        assert 2 == mock_timer.stop.call_count
        mock_timing.assert_called_with()
        assert 2 == mock_timing.call_count

    def test_zero_division_error(self):
        """ ZeroDivisionError is not raised when timing is 0.
        """
        from wheezy.core.benchmark import Benchmark

        t1 = Mock()
        t1.__name__ = "t1"
        mock_timer = Mock()
        mock_timer.timing = 0
        b = Benchmark((t1,), 10, timer=mock_timer)
        b.report("sample")

    def test_report(self):
        """ Ensure report is printed.
        """
        from wheezy.core.benchmark import Benchmark

        t1 = Mock()
        t1.__name__ = "t1"
        mock_timer = Mock()
        mock_timer.timing = 1
        b = Benchmark((t1,), 10, timer=mock_timer)
        b.report("sample")


class TimerTestCase(unittest.TestCase):
    def test_start_stop(self):
        """ Ensure a call is intercepted.
        """
        from wheezy.core.benchmark import Timer

        mock_target = Mock()
        mock_name = Mock()
        mock_target.name = mock_name
        t = Timer(mock_target, "name")
        t.start()
        assert mock_name != mock_target.name
        mock_target.name()
        t.stop()
        assert mock_name == mock_target.name
