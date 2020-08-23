""" ``retry`` module.
"""

from time import sleep, time


def make_retry(timeout, start, end=None, slope=1.0, step=0.0):
    """Return a function that accepts a single argument ``acquire`` which
    should be a callable (without any arguments) that returns a boolean
    value when attempt to acquire some resource or perform operation
    succeeded or not.

    If a first attempt fails the retry function sleeps for ``start``
    and later delay time is increased linearly per ``slope`` and
    ``step`` until ``end``. A last delay is a time remaining.
    A total retry time is limited by ``timeout``.

    ``timeout`` -  a number of seconds for the entire retry operation
    from the first failed attempt to the last (excluding time for both
    acquire operations).

    ``start`` -  a time for initial delay.

    ``end`` - a time for a longest delay between retry attempts.

    ``slope`` and ``step`` - coefficients for linear calculation of
    the next delay.

    Example 1::

        # delays: 0.5, 0.5, 0.5, 0.5
        retry = make_retry(timeout=10.0, start=0.5)

    Example 2::

        # delays: 0.5, 0.1, 1.5, 2.0
        retry = make_retry(timeout=10.0, start=0.5, end=2.0, step=0.5)

    Example 3::

        # delays: 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 2.0
        retry = make_retry(timeout=10.0, start=0.05, end=2.0, slope=2.0)
        if retry(lambda: acquire('something')):
            # good to go
        else:
            # timed out
    """
    end = end is None and start or end
    assert timeout > 0.0
    assert start >= 0.0
    assert end >= 0.0
    assert timeout > end
    assert slope >= 1.0
    assert step >= 0.0
    assert start <= end

    def retry(acquire):
        if acquire():
            return True
        expires = time() + timeout
        delay = start
        sleep(delay)
        while True:
            if acquire():
                return True
            remains = expires - time()
            if remains < delay:
                break
            if delay < end:
                delay = delay * slope + step
                if delay > end:
                    delay = end
            sleep(delay)
        if remains <= 0.0:
            return False
        sleep(remains)
        return acquire()

    return retry
