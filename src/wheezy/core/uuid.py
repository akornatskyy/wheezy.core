
""" ``uuid`` module.
"""

from base64 import b64decode
from base64 import b64encode

from wheezy.core.introspection import import_name

UUID = import_name('uuid.UUID')
UUID_EMPTY = UUID('00000000-0000-0000-0000-000000000000')


def shrink_uuid(uuid):
    """
        >>> shrink_uuid(UUID('a4af2f54-e988-4f5c-bfd6-351c79299b74'))
        'pK8vVOmIT1y_1jUceSmbdA'
        >>> shrink_uuid(UUID('d17aba88-19c3-400e-adee-3ecf935db272'))
        '0Xq6iBnDQA6t7j7Pk12ycg'
        >>> shrink_uuid(UUID('39ae13ee-202a-42d1-9117-6fb6fdd169a4'))
        'Oa4T7iAqQtGRF2-2_dFppA'
        >>> shrink_uuid(UUID_EMPTY)
        'AAAAAAAAAAAAAAAAAAAAAA'
    """
    assert isinstance(uuid, UUID)
    return b64encode(uuid.bytes, '-_')[:22]


def parse_uuid(s):
    """
        >>> parse_uuid('pK8vVOmIT1y_1jUceSmbdA')
        UUID('a4af2f54-e988-4f5c-bfd6-351c79299b74')
        >>> parse_uuid('0Xq6iBnDQA6t7j7Pk12ycg')
        UUID('d17aba88-19c3-400e-adee-3ecf935db272')
        >>> parse_uuid('Oa4T7iAqQtGRF2-2_dFppA')
        UUID('39ae13ee-202a-42d1-9117-6fb6fdd169a4')
        >>> parse_uuid('AAAAAAAAAAAAAAAAAAAAAA')
        UUID('00000000-0000-0000-0000-000000000000')

        Return an empty uuid in case the string is empty of length
        not equal to 22.

        >>> parse_uuid('')
        UUID('00000000-0000-0000-0000-000000000000')
        >>> parse_uuid('x')
        UUID('00000000-0000-0000-0000-000000000000')

        Incorrect base64 padding.

        >>> parse_uuid('AAAAAAAAAA*AAAAAAAAAAA')
        UUID('00000000-0000-0000-0000-000000000000')
    """
    if not s or len(s) != 22:
        return UUID_EMPTY
    try:
        raw = b64decode(s + '==', '-_')
    except TypeError:  # Incorrect padding
        return UUID_EMPTY
    assert len(raw) == 16
    return UUID(bytes=raw)
