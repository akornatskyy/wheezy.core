"""
"""

import unittest


class GzipTestCase(unittest.TestCase):
    def test_compress_decompress(self):
        """ Ensure decompress is a reverse function of compress.
        """
        from wheezy.core.comp import bton, ntob
        from wheezy.core.gzip import compress, decompress

        c = compress(ntob("test", "utf-8"))
        assert "test" == bton(decompress(c), "utf-8")
