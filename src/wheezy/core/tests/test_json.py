
""" ``test_json`` module.
"""

import unittest

from decimal import Decimal

from wheezy.core.json import json_encode
from wheezy.core.json import json_decode
from wheezy.core.json import date
from wheezy.core.json import datetime
from wheezy.core.json import time

try:
    json_encode({})

    class JSONEncodeTestCase(unittest.TestCase):
        """ Test the ``json_encode`` function.
        """

        def test_encode_date(self):
            self.assertEqual(
                    json_encode({'d': date(2012, 2, 22)}),
                    '{"d":"2012-02-22"}')
            self.assertEqual(
                    json_encode({'d': date.min}),
                    '{"d":""}')

        def test_encode_datetime(self):
            self.assertEqual(
                    json_encode({'d': datetime(2012, 2, 22)}),
                    '{"d":"2012-02-22T00:00:00"}')
            self.assertEqual(
                    json_encode({'d': datetime(2012, 2, 22, 14, 17, 39)}),
                    '{"d":"2012-02-22T14:17:39"}')
            self.assertEqual(
                    json_encode({'d': datetime.min}),
                    '{"d":""}')

        def test_encode_time(self):
            self.assertEqual(
                    json_encode({'d': time(14, 17, 39, 422)}),
                    '{"d":"14:17:39"}')

        def test_encode_decimal(self):
            self.assertEqual(
                    json_encode({'d': Decimal('14.79')}),
                    '{"d":"14.79"}')

        def test_encode_unicode(self):
            from wheezy.core.comp import u
            self.assertEqual(
                    json_encode({'d': u('x')}),
                    '{"d":"x"}')

        def test_forward_slashes_escaped(self):
            self.assertEqual(
                    json_encode({'d': '</script>'}),
                    '{"d":"<\\/script>"}')

    class JSONDecodeTestCase(unittest.TestCase):
        """ Test the ``json_encode`` function.
        """

        def test_decode_date(self):
            from wheezy.core.comp import u
            d = json_decode('{"d": "2012-02-22"}')
            self.assertEqual(u('2012-02-22'), d['d'])

        def test_decode_decimal(self):
            d = json_decode('{"d": 12.79}')
            self.assertTrue(isinstance(d['d'], Decimal))

except NotImplementedError:
    pass