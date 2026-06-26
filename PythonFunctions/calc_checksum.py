def calc_checksum(ascii_msg: str) -> str:
    """
    RMU checksum: sum of ASCII byte values modulo 256, as 2-digit uppercase hex.
    Covers message_type + command_id + payload (excludes ^ start and ~ stop chars).
    """
    msg_bytes = bytearray(ascii_msg, "ascii")
    checksum_bytes = b'%02X' % (sum(msg_bytes) & 0xFF)
    return checksum_bytes.decode("ascii")
