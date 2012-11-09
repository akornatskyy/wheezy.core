
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

            assert looks(Foo).like(IFoo, ignore_funcs='foo')

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

            assert looks(Foo).like(IFoo, ignore_argspec='foo')

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

        def test_inheritance(self):
            """ Test inheritance use case.
            """
            from wheezy.core.introspection import looks

            class IFoo(object):
                def foo(self):
                    pass

            class IBar(IFoo):
                def bar(self):
                    pass

            class Bar(IBar):
                def foo(self):
                    pass

                def bar(self):
                    pass

            assert looks(Bar).like(IBar)
            assert looks(Bar).like(IFoo)

        def test_special_method(self):
            """ Test if __?__ are checked
            """
            from wheezy.core.introspection import looks

            class IFoo(object):
                def __len__(self):
                    pass

            class Foo(IFoo):
                pass

            assert looks(Foo).like(IFoo)
            assert not looks(Foo).like(IFoo, notice=['__len__'])
            self.assert_warning("'__len__': is missing.")

            class Foo(IFoo):
                def __len__(self):
                    pass

            assert looks(Foo).like(IFoo)
            assert looks(Foo).like(IFoo, notice=['__len__'])

        def test_decorator(self):
            """
            """
            from wheezy.core.introspection import looks

            def bar():
                def decorate(m):
                    def x(*args, **kwargs):
                        pass
                    return x
                return decorate

            class IFoo(object):
                def foo(self, a):
                    pass

            class Foo(object):
                @bar()
                def foo(self, a):
                    pass

            assert not looks(Foo).like(IFoo)
            self.assert_warning("'foo': argument names or defaults "
                                "have no match.")

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
