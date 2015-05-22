
""" ``retry`` module.
"""

from time import time
from time import sleep


def make_retry(timeout, min_delay, slope, delta, max_delay):
    """ Return a function that accepts a single argument ``acquire`` which
        should be a callable (without any arguments) that returns a boolean
        value when attempt to acquire some resource or perform operation
        succeeded or not.

        If a first attempt fails the retry function sleeps for ``min_delay``
        and later delay time is increased linearly per  ``slope`` and
        ``delta`` until ``max_delay``. A last delay is a time remaining.
        A total retry time is limited by ``timeout``.

        ``timeout`` -  a number of seconds for the entire retry operation
        from the first failed attempt to the last (excluding time for both
        acquire operations).

        ``min_delay`` -  a time for initial delay.

        ``slope`` and ``delta`` - coefficients for linear calculation of
        the next delay.

        ``max_delay`` - a time for a longest delay between retry attempts.


        Example 1::

            # delays: 0.5, 0.1, 1.5, 2.0
            retry = make_retry(timeout=10.0, min_delay=0.5, slope=1.0,
                               delta=0.5, max_delay=2.0)

        Example 2::

            # delays: 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 2.0
            retry = make_retry(timeout=10.0, min_delay=0.05, slope=2.0,
                               delta=0.0, max_delay=2.0)
            if retry(lambda: acquire('something')):
                # good to go
            else:
                # timed out
    """
    assert timeout > 0.0
    assert min_delay > 0.0
    assert max_delay > 0.0
    assert timeout > min_delay
    assert timeout > max_delay

    def retry(acquire):
        if acquire():
            return True
        expires = time() + timeout
        delay = min_delay
        sleep(delay)
        while True:
            if acquire():
                return True
            remains = expires - time()
            if remains < delay:
                break
            if delay < max_delay:
                delay = delay * slope + delta
                if delay > max_delay:
                    delay = max_delay
            sleep(delay)
        if remains <= 0.0:
            return False
        sleep(remains)
        return acquire()
    return retry
