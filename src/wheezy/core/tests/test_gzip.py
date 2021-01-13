"""
"""

import unittest

from wheezy.core.gzip import compress, decompress


class GzipTestCase(unittest.TestCase):
    def test_compress_decompress(self):
        """Ensure decompress is a reverse function of compress."""
        c = compress("test".encode("utf-8"))
        assert "test" == decompress(c).decode("utf-8")
