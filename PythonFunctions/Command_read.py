from calc_checksum import calc_checksum


def command_read(message_type: str, command_id: str, dest_addr: int,
                 table: int, block: int, offset: int, bytes_val: int) -> str:
    hex_dest_addr = f"{dest_addr:02X}"
    hex_table     = f"{table:02X}"
    hex_block     = f"{block:02X}"
    hex_offset    = f"{offset:02X}"
    hex_bytes     = f"{bytes_val:02X}"

    payload  = hex_dest_addr + hex_table + hex_block + hex_offset + hex_bytes
    checksum = calc_checksum(message_type + command_id + payload)

    return "^" + message_type + command_id + payload + checksum + "~"
