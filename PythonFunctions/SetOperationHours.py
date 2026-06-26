import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Command_set import command_set


def SetOperationHours(MeasValue: int) -> str:
    return command_set(
        message_type='@',
        command_id='99',
        dest_addr=0x30,
        table=18,
        block=6,
        offset=0,
        bytes_val=2,
        value=MeasValue,
        format_txt='UI',
        divisor=1,
    )
