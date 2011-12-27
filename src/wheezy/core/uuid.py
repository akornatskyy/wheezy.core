
""" ``uuid`` module.
"""

from base64 import b64decode
from base64 import b64encode
from binascii import Error

from wheezy.core.comp import b
from wheezy.core.introspection import import_name


BASE64_ALTCHARS = b('-_')
BASE64_SUFFIX = b('==')
UUID = import_name('uuid.UUID')
UUID_EMPTY = UUID('00000000-0000-0000-0000-000000000000')


def shrink_uuid(uuid):
    """
        >>> from wheezy.core.comp import n
        >>> n(shrink_uuid(UUID('a4af2f54-e988-4f5c-bfd6-351c79299b74')))
        'pK8vVOmIT1y_1jUceSmbdA'
        >>> n(shrink_uuid(UUID('d17aba88-19c3-400e-adee-3ecf935db272')))
        '0Xq6iBnDQA6t7j7Pk12ycg'
        >>> n(shrink_uuid(UUID('39ae13ee-202a-42d1-9117-6fb6fdd169a4')))
        'Oa4T7iAqQtGRF2-2_dFppA'
        >>> n(shrink_uuid(UUID_EMPTY))
        'AAAAAAAAAAAAAAAAAAAAAA'
    """
    assert isinstance(uuid, UUID)
    return b64encode(uuid.bytes, BASE64_ALTCHARS)[:22]


def parse_uuid(s):
    """
        >>> from wheezy.core.comp import n
        >>> n(parse_uuid(b('pK8vVOmIT1y_1jUceSmbdA')))
        UUID('a4af2f54-e988-4f5c-bfd6-351c79299b74')
        >>> n(parse_uuid(b('0Xq6iBnDQA6t7j7Pk12ycg')))
        UUID('d17aba88-19c3-400e-adee-3ecf935db272')
        >>> n(parse_uuid(b('Oa4T7iAqQtGRF2-2_dFppA')))
        UUID('39ae13ee-202a-42d1-9117-6fb6fdd169a4')
        >>> n(parse_uuid(b('AAAAAAAAAAAAAAAAAAAAAA')))
        UUID('00000000-0000-0000-0000-000000000000')

        Return an empty uuid in case the string is empty of length
        not equal to 22.

        >>> n(parse_uuid(b('')))
        UUID('00000000-0000-0000-0000-000000000000')
        >>> n(parse_uuid(b('x')))
        UUID('00000000-0000-0000-0000-000000000000')

        Incorrect base64 padding.

        >>> n(parse_uuid(b('AAAAAAAAAA*AAAAAAAAAAA')))
        UUID('00000000-0000-0000-0000-000000000000')
    """
    if not s or len(s) != 22:
        return UUID_EMPTY
    try:
        raw = b64decode(s + BASE64_SUFFIX, BASE64_ALTCHARS)
    except (TypeError, Error):  # Incorrect padding
        return UUID_EMPTY
    assert len(raw) == 16
    return UUID(bytes=raw)
