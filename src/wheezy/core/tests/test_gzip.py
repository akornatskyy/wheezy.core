
"""
"""

import unittest


class GzipTestCase(unittest.TestCase):

    def test_compress_decompress(self):
        """ Ensure decompress is a reverse function of compress.
        """
        from wheezy.core.gzip import compress
        from wheezy.core.gzip import decompress
        assert 'test' == decompress(compress('test'))
