## Checksum Calculation Function

```
def calc_checksum(ascii_msg:str) -> str:
    """
    Calculate the checksum for RMU ASCII message

    Args:
        ascii_msg: RMU ASCII message in string
    Returns:
        checksum: checksum in string
    """
    # convert ascii message into bytearray
    msg_bytes = bytearray(ascii_msg, "ascii")
    # calculate the checksum in bytes
    checksum_bytes = b'%02X' % (sum(msg_bytes) & 0xFF)
    # convert checksum from bytes to ascii string
    checksum = checksum_bytes.decode("ascii")
    return checksum
```

## Command Set 

```
def command_set(message_type: str, 
                command_id: str,
                dest_addr: int,
                table: int, 
                block: int, 
                offset: int, 
                bytes_val: int, 
                value) -> str:
    """
    Creates a hex string from decimal values (2 digits each), value payload, appends a checksum, and adds "~" at the end.

    Args:
        message_type: String prefix (e.g., "Header").
        table: Decimal value for Table.
        block: Decimal value for Block.
        offset: Decimal value for Offset.
        bytes_val: Decimal value for Bytes.
        value: Human readable value for Value.

    Returns:
        Hex string with checksum and "~" suffix.
    """
    # start character: ASCII character ‘^’ (0x5E)
    start_char = "^"
        
    # Convert decimal values to 2-digit hex strings (uppercase, no 0x prefix)
    hex_dest_addr = f"{dest_addr:02X}"
    hex_table = f"{table:02X}"
    hex_block = f"{block:02X}"
    hex_offset = f"{offset:02X}"
    hex_bytes = f"{bytes_val:02X}"

    # TODO: implement the conversion from human readable value to hex depending on data type, length, signed or not, divisor
    hex_value = f"{value:02X}"

    # zero padding the remaining space to have a total of 32 bytes
    hex_value_payload = hex_value.ljust(64, '0')

    # Build the hex string payload
    payload = hex_dest_addr + hex_table + hex_block + hex_offset + hex_bytes + hex_value_payload

    # Calculate checksum: summation of the preceding bytes, starting from message type, ending with the last payload byte before checksum
    checksum = calc_checksum(message_type + command_id + payload)

    # stop character: ASCII ‘~’ (0x7E)
    stop_char = "~"

    # create command
    rmu_command = start_char + message_type + command_id + payload + checksum + stop_char
    return rmu_command
```

## To call this command set function:

```
# Example: set the hour on controller clock to 12
command_set(message_type='@',
            command_id='99',
            dest_addr=48,
            table=3, 
            block=1, 
            offset=0, 
            bytes_val=1, 
            value=12)
```

## Command Read

```
def command_read(message_type: str, 
                command_id: str,
                dest_addr: int,
                table: int, 
                block: int, 
                offset: int, 
                bytes_val: int) -> str:
    """
    Creates a hex string from decimal values (2 digits each), appends a checksum, and adds "~" at the end.
    Note: This function does not include the "Value" parameter.

    Args:
        header_read: String prefix (e.g., "Header").
        table: Decimal value for Table.
        block: Decimal value for Block.
        offset: Decimal value for Offset.
        bytes_val: Decimal value for Bytes.

    Returns:
        Hex string with checksum and "~" suffix.
    """
    # start character: ASCII character ‘^’ (0x5E)
    start_char = "^"
        
    # Convert decimal values to 2-digit hex strings (uppercase, no 0x prefix)
    hex_dest_addr = f"{dest_addr:02X}"
    hex_table = f"{table:02X}"
    hex_block = f"{block:02X}"
    hex_offset = f"{offset:02X}"
    hex_bytes = f"{bytes_val:02X}"

    # Build the hex string payload
    payload = hex_dest_addr + hex_table + hex_block + hex_offset + hex_bytes

    # Calculate checksum: summation of the preceding bytes, starting from message type, ending with the last payload byte before checksum
    checksum = calc_checksum(message_type + command_id + payload)

    # stop character: ASCII ‘~’ (0x7E)
    stop_char = "~"

    # create command
    rmu_command = start_char + message_type + command_id + payload + checksum + stop_char
    return rmu_command
```

## To call this command read function:

```
# Example: read controller clock's hour
command_read(message_type='?',
            command_id='99',
            dest_addr=48,
            table=3, 
            block=1, 
            offset=0, 
            bytes_val=1)
```

## Read Expected

```
def read_expected(message_type: str, 
                command_id: str,
                dest_addr: int,
                table: int, 
                block: int, 
                offset: int, 
                bytes_val: int,
                value) -> str:
    """
    Creates a hex string from decimal values (2 digits each), value payload, appends a checksum, and adds "~" at the end.

    Args:
        header_read: String prefix (e.g., "Header").
        table: Decimal value for Table.
        block: Decimal value for Block.
        offset: Decimal value for Offset.
        bytes_val: Decimal value for Bytes.
        value: Decimal value for Value.

    Returns:
        Hex string with checksum and "~" suffix.
    """
    # status: ASCII character ‘%’ = Acknowledgement (ACK); ASCII character ‘&’ = Negative Acknowledgement (NAK)
    status = "%"

    # start character: ASCII character ‘^’ (0x5E)
    start_char = "^"

    # Convert decimal values to 2-digit hex strings (uppercase, no 0x prefix)
    hex_dest_addr = f"{dest_addr:02X}"
    hex_table = f"{table:02X}"
    hex_block = f"{block:02X}"
    hex_offset = f"{offset:02X}"
    hex_bytes = f"{bytes_val:02X}"
    
    # TODO: implement the conversion from human readable value to hex depending on data type, length, signed or not, divisor
    hex_value = f"{value:02X}"

    # zero padding the remaining space to have a total of 32 bytes
    hex_value_payload = hex_value.ljust(64, '0')

    # Build the hex string payload
    payload = hex_dest_addr + hex_table + hex_block + hex_offset + hex_bytes + hex_value_payload

    # Calculate checksum: summation of the preceding bytes, starting from message type, ending with the last payload byte before checksum
    checksum = calc_checksum(message_type + command_id + payload)

    # stop character: ASCII ‘~’ (0x7E)
    stop_char = "~"

    # create expected response
    rmu_expected_response = status + start_char + message_type + command_id + payload + checksum + stop_char
    return rmu_expected_response
```

The above function returns the expected response when the command is correctly composed and values accepted by the controller. This function is for positive testing NOT negative testing. 

## To call this read expected function:

```
# Example: the expected response showing controller clock's hour at 12
read_expected(message_type='?',
            command_id='99',
            dest_addr=48,
            table=3, 
            block=1, 
            offset=0, 
            bytes_val=1, 
            value=12)
```





# Value to Hex Conversion

```
import struct                           # python built-in

def cast_data_encode(data, type, divisor):
    """
    Cast data
    """
    if type == int:
        data = float(data)
        data = int(data * divisor)
    elif type == float:
        data = float(data)
    elif type == str:
        data = str(data)
    return data

def charSignedToHex(value:int, littleEndian=True):
    """
    Convert signed char to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'b'
    return bytes(struct.pack(format, value)).hex()

def charUnsignedToHex(value:int, littleEndian=True):
    """
    Convert unsigned char to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'B'
    return bytes(struct.pack(format, value)).hex()

def shortSignedToHex(value:int, littleEndian=True):
    """
    Convert signed short to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'h'
    return bytes(struct.pack(format, value)).hex()

def shortUnsignedToHex(value:int, littleEndian=True):
    """
    Convert unsigned short to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'H'
    return bytes(struct.pack(format, value)).hex()

def longSignedToHex(value:int, littleEndian=True):
    """
    Convert signed long tohex string
    """
    format = '<' if littleEndian else '>'
    format += 'l'
    return bytes(struct.pack(format, value)).hex()

def longUnsignedToHex(value:int, littleEndian=True):
    """
    Convert unsigned long to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'L'
    return bytes(struct.pack(format, value)).hex()

def longLongSignedToHex(value:int, littleEndian=True):
    """
    Convert signed long long to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'q'
    return bytes(struct.pack(format, value)).hex()

def longLongUnsignedToHex(value:int, littleEndian=True):
    """
    Convert unsigned long long to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'Q'
    return bytes(struct.pack(format, value)).hex()

def floatToHex(value:float, littleEndian=True):
    """
    Convert float to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'f'
    return bytes(struct.pack(format, value)).hex()

def doubleToHex(value:float, littleEndian=True):
    """
    Convert double to hex string
    """
    format = '<' if littleEndian else '>'
    format += 'd'
    return bytes(struct.pack(format, value)).hex()

def ASCIIStrToHex(value:str):
    """
    Convert a string of text to hex
    """
    return value.encode().hex()

class TBOConverter:

    # dictionary mapping number of bytes to signed integer -> hex converter
    converters_signedIntToHex = {1: charSignedToHex,
                                2: shortSignedToHex,
                                4: longSignedToHex,
                                8: longLongSignedToHex}

    # dictionary mapping number of bytes to unsigned integer -> hex converter
    converters_unsignedIntToHex = {1: charUnsignedToHex,
                                2: shortUnsignedToHex,
                                4: longUnsignedToHex,
                                8: longLongUnsignedToHex}

    # dictionary mapping number of bytes to float -> hex converter
    converters_floatToHex = {4: floatToHex,
                            8: doubleToHex}

    def getToHexConverter(type, numBytes:int, signed):
        """
        Get the Converter based on data type, number of bytes, and signed boolean
    
        Args:
            type: data type, int or float
            numBytes: number of bytes
            signed: boolean indicating whether signed or unsigned
        Returns:
            converter: a converter function
        """
        converter = lambda data, littleEndian=False: data
    
        if type is int:
            if numBytes not in (1, 2, 4, 8):
                raise ValueError(f"Invalid length. Expecting: 1, 2, 4, or 8")
            if signed:
                converter = TBOConverter.converters_signedIntToHex.get(numBytes)
            else:
                converter = TBOConverter.converters_unsignedIntToHex.get(numBytes)
        elif type is float:
            converter = TBOConverter.converters_floatToHex.get(numBytes)
        elif type is str:
            converter = lambda data, littleEndian=False: ASCIIStrToHex(data)
        else:
            raise ValueError(f"Invalid type. Expecting type to be int, float, or str, but got {type}")
        
        return converter

def encode_data(data, type, length, signed, divisor=1, little_endian=False):
    """
    Encode the given data into a hex string based on spec and return encoded data
    """
    data = cast_data_encode(data, type, divisor)
    data_hex = TBOConverter.getToHexConverter(type, length, signed)(data, little_endian)
    return data_hex
```

## Example function call:

```
# Example: convert 12 to signed one-byte integer
encode_data(data=12, 
            type=int,
            length=1,
            signed=True)

# Example: convert 20.5 to float
encode_data(data=20.5, 
            type=float,
            length=4,
            signed=True)
```

Note: input arg type should be python class: int, float, or str