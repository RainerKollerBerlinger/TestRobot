import struct


def cast_data_encode(data, type, divisor):
    if type == int:
        data = float(data)
        data = int(data * divisor)
    elif type == float:
        data = float(data)
    elif type == str:
        data = str(data)
    return data


def charSignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'b'
    return bytes(struct.pack(fmt, value)).hex()


def charUnsignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'B'
    return bytes(struct.pack(fmt, value)).hex()


def shortSignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'h'
    return bytes(struct.pack(fmt, value)).hex()


def shortUnsignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'H'
    return bytes(struct.pack(fmt, value)).hex()


def longSignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'l'
    return bytes(struct.pack(fmt, value)).hex()


def longUnsignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'L'
    return bytes(struct.pack(fmt, value)).hex()


def longLongSignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'q'
    return bytes(struct.pack(fmt, value)).hex()


def longLongUnsignedToHex(value: int, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'Q'
    return bytes(struct.pack(fmt, value)).hex()


def floatToHex(value: float, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'f'
    return bytes(struct.pack(fmt, value)).hex()


def doubleToHex(value: float, littleEndian=True):
    fmt = ('<' if littleEndian else '>') + 'd'
    return bytes(struct.pack(fmt, value)).hex()


def ASCIIStrToHex(value: str):
    return value.encode().hex()


class TBOConverter:
    converters_signedIntToHex = {
        1: charSignedToHex,
        2: shortSignedToHex,
        4: longSignedToHex,
        8: longLongSignedToHex,
    }
    converters_unsignedIntToHex = {
        1: charUnsignedToHex,
        2: shortUnsignedToHex,
        4: longUnsignedToHex,
        8: longLongUnsignedToHex,
    }
    converters_floatToHex = {
        4: floatToHex,
        8: doubleToHex,
    }

    @staticmethod
    def getToHexConverter(type, numBytes: int, signed):
        if type is int:
            if numBytes not in (1, 2, 4, 8):
                raise ValueError(f"Invalid length {numBytes}. Expecting: 1, 2, 4, or 8")
            if signed:
                return TBOConverter.converters_signedIntToHex[numBytes]
            else:
                return TBOConverter.converters_unsignedIntToHex[numBytes]
        elif type is float:
            return TBOConverter.converters_floatToHex[numBytes]
        elif type is str:
            return lambda data, littleEndian=True: ASCIIStrToHex(data)
        else:
            raise ValueError(f"Invalid type {type}. Expecting int, float, or str")


def encode_data(data, type, length: int, signed: bool, divisor=1, little_endian=True) -> str:
    data = cast_data_encode(data, type, divisor)
    return TBOConverter.getToHexConverter(type, length, signed)(data, little_endian).upper()


# Maps FormatTXT from the Excel command repository to (python type, signed)
_FORMAT_MAP = {
    'UB': (int,   False),
    'UI': (int,   False),
    'SI': (int,   True),
    'FL': (float, False),
}


def value_to_hex(value, format_txt: str, bytes_val: int, divisor=1) -> str:
    """
    Convert a human-readable value to its hex string representation.

    Uses the FormatTXT and DivisorTXT from the Excel command repository to
    select the correct encoding. UB fields with bytes_val > 1 are treated
    as ASCII strings (e.g. serial numbers).
    """
    if format_txt not in _FORMAT_MAP:
        raise ValueError(f"Unknown FormatTXT: {format_txt!r}. Expected one of {list(_FORMAT_MAP)}")

    py_type, signed = _FORMAT_MAP[format_txt]

    # Multi-byte UB fields store ASCII strings (e.g. serial numbers)
    if format_txt == 'UB' and bytes_val > 1:
        py_type = str

    return encode_data(data=value, type=py_type, length=bytes_val, signed=signed,
                       divisor=float(divisor))
