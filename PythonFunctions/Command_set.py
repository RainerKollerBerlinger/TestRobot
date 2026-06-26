from calc_checksum import calc_checksum
from value_to_hex import value_to_hex


def command_set(message_type: str, command_id: str, dest_addr: int,
                table: int, block: int, offset: int,
                bytes_val: int, value,
                format_txt: str, divisor=1) -> str:
    hex_dest_addr = f"{dest_addr:02X}"
    hex_table     = f"{table:02X}"
    hex_block     = f"{block:02X}"
    hex_offset    = f"{offset:02X}"
    hex_bytes     = f"{bytes_val:02X}"
    hex_value     = value_to_hex(value, format_txt, bytes_val, divisor)

    hex_value_payload = hex_value.ljust(64, '0')

    payload  = hex_dest_addr + hex_table + hex_block + hex_offset + hex_bytes + hex_value_payload
    checksum = calc_checksum(message_type + command_id + payload)

    return "^" + message_type + command_id + payload + checksum + "~"
