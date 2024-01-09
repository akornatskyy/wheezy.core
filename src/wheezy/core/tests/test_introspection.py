""" Unit tests for ``wheezy.core.introspection``.
"""

import unittest

from wheezy.core.descriptors import attribute
from wheezy.core.introspection import looks


class LooksLike(object):
    def assert_warning(self, msg):
        print([str(w.message) for w in self.w])
        assert len(self.w) == 1
        self.assertEqual(msg, str(self.w[-1].message))

    def test_func(self):
        """Tests if there is any function missing."""

        class IFoo(object):
            def foo(self):
                pass  # pragma: nocover

        class Foo(object):
            def bar(self):
                pass  # pragma: nocover

        assert not looks(Foo).like(IFoo)
        self.assert_warning("'foo': is missing.")

    def test_ignore_func(self):
        """Tests if function is ignored."""

        class IFoo(object):
            def foo(self):
                pass  # pragma: nocover

        class Foo(object):
            def bar(self):
                pass  # pragma: nocover

        assert looks(Foo).like(IFoo, ignore_funcs=["foo"])

    def test_redundant_ignore(self):
        """Tests function is set to be ignored but it is not found."""

        class IFoo(object):
            def bar(self):
                pass  # pragma: nocover

        class Foo(object):
            def bar(self):
                pass  # pragma: nocover

        assert not looks(Foo).like(IFoo, ignore_funcs=["foo"])
        self.assert_warning("'foo': redundant ignore.")

    def test_args(self):
        """Tests if there any function args corresponds."""

        class IFoo(object):
            def foo(self, a, b=1):
                pass  # pragma: nocover

        class Foo(object):
            def foo(self, a, b):
                pass  # pragma: nocover

        assert not looks(Foo).like(IFoo)
        self.assert_warning(
            "'foo': argument names or defaults " "have no match."
        )

    def test_ignore_args(self):
        """Tests if function args ignored."""

        class IFoo(object):
            def foo(self, a, b=1):
                pass  # pragma: nocover

        class Foo(object):
            def foo(self, a, b):
                pass  # pragma: nocover

        assert looks(Foo).like(IFoo, ignore_argspec="foo")

    def test_property(self):
        """Tests if there any @property corresponds."""

        class IFoo(object):
            @property
            def foo(self):
                pass  # pragma: nocover

        class Foo(object):
            def foo(self):
                pass  # pragma: nocover

        assert not looks(Foo).like(IFoo)
        self.assert_warning("'foo': is not property.")

    def test_inheritance(self):
        """Test inheritance use case."""

        class IFoo(object):
            def foo(self):
                pass  # pragma: nocover

        class IBar(IFoo):
            def bar(self):
                pass  # pragma: nocover

        class Bar(IBar):
            def foo(self):
                pass  # pragma: nocover

            def bar(self):
                pass  # pragma: nocover

        assert looks(Bar).like(IBar)
        assert looks(Bar).like(IFoo)

    def test_special_method(self):
        """Test if __?__ are checked"""

        class IFoo(object):
            def __len__(self):
                pass  # pragma: nocover

        class Foo(IFoo):
            pass  # pragma: nocover

        assert looks(Foo).like(IFoo)
        assert not looks(Foo).like(IFoo, notice=["__len__"])
        self.assert_warning("'__len__': is missing.")

        class Foo(IFoo):
            def __len__(self):
                pass  # pragma: nocover

        assert looks(Foo).like(IFoo)
        assert looks(Foo).like(IFoo, notice=["__len__"])

    def test_decorator(self):
        """Decorator argspec doesn't match."""

        def bar():
            def decorate(m):
                def x(*args, **kwargs):
                    pass  # pragma: nocover

                return x

            return decorate

        class IFoo(object):
            def foo(self, a):
                pass  # pragma: nocover

        class Foo(object):
            @bar()
            def foo(self, a):
                pass  # pragma: nocover

        assert not looks(Foo).like(IFoo)
        self.assert_warning(
            "'foo': argument names or defaults " "have no match."
        )

    def test_type(self):
        """Test if decorator types do not match."""

        class IFoo(object):
            @attribute
            def foo(self):
                pass  # pragma: nocover

        class Foo(IFoo):
            @property
            def foo(self):
                pass  # pragma: nocover

        assert not looks(Foo).like(IFoo)
        self.assert_warning("'foo': is not attribute.")

    def test_various(self):
        """Tests if there are no errors."""

        class IFoo(object):
            def foo(self, a, b=1):
                pass  # pragma: nocover

            @property
            def bar(self):
                pass  # pragma: nocover

        class Foo(object):
            def foo(self, a, b=1):
                pass  # pragma: nocover

            @property
            def bar(self):
                pass  # pragma: nocover

        assert looks(Foo).like(IFoo)
        assert len(self.w) == 0


try:
    import warnings
except ImportError:  # pragma: nocover
    pass
else:

    class LooksLikeTestCase(unittest.TestCase, LooksLike):
        def setUp(self):
            warnings.resetwarnings()
            self.ctx = warnings.catch_warnings(record=True)
            self.w = self.ctx.__enter__()

        def tearDown(self):
            self.ctx.__exit__(None, None, None)
