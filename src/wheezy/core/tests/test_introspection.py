
""" Unit tests for ``wheezy.core.introspection``.
"""

import unittest

try:
    from warnings import catch_warnings
except ImportError:
    pass
else:

    class LooksLikeTestCase(unittest.TestCase):

        def setUp(self):
            self.ctx = catch_warnings(record=True)
            self.w = self.ctx.__enter__()

        def tearDown(self):
            self.ctx.__exit__(None, None, None)

        def assert_warning(self, msg):
            assert len(self.w) == 1
            self.assertEquals(msg, str(self.w[-1].message))

        def test_func(self):
            """ Tests if there is any function missing.
            """
            from wheezy.core.introspection import looks

            class IFoo(object):
                def foo(self):
                    pass

            class Foo(object):
                def bar(self):
                    pass

            assert not looks(Foo).like(IFoo)
            self.assert_warning("'foo': is missing.")

        def test_ignore_func(self):
            """ Tests if function is ignored.
            """
            from wheezy.core.introspection import looks

            class IFoo(object):
                def foo(self):
                    pass

            class Foo(object):
                def bar(self):
                    pass

            assert looks(Foo, ignore_funcs='foo').like(IFoo)

        def test_args(self):
            """ Tests if there any function args corresponds.
            """
            from wheezy.core.introspection import looks

            class IFoo(object):
                def foo(self, a, b=1):
                    pass

            class Foo(object):
                def foo(self, a, b):
                    pass

            assert not looks(Foo).like(IFoo)
            self.assert_warning("'foo': argument names or defaults "
                                "have no match.")

        def test_ignore_args(self):
            """ Tests if function args ignored.
            """
            from wheezy.core.introspection import looks

            class IFoo(object):
                def foo(self, a, b=1):
                    pass

            class Foo(object):
                def foo(self, a, b):
                    pass

            assert looks(Foo, ignore_argspec='foo').like(IFoo)

        def test_decorator(self):
            """ Tests if there any method decorators corresponds.
            """
            from wheezy.core.introspection import looks

            class IFoo(object):
                @property
                def foo(self):
                    pass

            class Foo(object):
                def foo(self):
                    pass

            assert not looks(Foo).like(IFoo)
            self.assert_warning("'foo': is not property.")

        def test_various(self):
            """ Tests if there are no errors.
            """
            from wheezy.core.introspection import looks

            class IFoo(object):

                def foo(self, a, b=1):
                    pass

                @property
                def bar(self):
                    pass

            class Foo(object):
                def foo(self, a, b=1):
                    pass

                @property
                def bar(self):
                    pass

            assert looks(Foo).like(IFoo)
            assert len(self.w) == 0
