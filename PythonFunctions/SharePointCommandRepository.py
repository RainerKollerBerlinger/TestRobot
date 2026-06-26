import os
import sys
import msal
import requests

# PythonFunctions/ — for sibling helpers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# lib/ — for config.py (which loads credentials.py)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))

from Command_set import command_set
from Command_read import command_read
from Read_Expected import read_expected
import config

# RMU protocol constants
COMMAND_ID    = '99'
MSG_TYPE_SET  = '@'
MSG_TYPE_READ = '?'
DEST_ADDR     = 0x30  # 48 decimal

# Fields to request from CommandLimits (one row per BlockCmdID × LimitType)
_COMMAND_LIMITS_FIELDS = [
    "LimitType",
    "MeasValue",
    "TeleExpected",
    "CloudExpected",
    "LUBlockCommandTitleLookupId",
]


class SharePointCommandRepository:
    """Robot Framework library that loads the command repository from SharePoint.

    Drop-in replacement for ExcelCommandRepository — same load_commands() /
    get_step() interface, so only the Library line in test_keywords.robot changes.

    Credentials are read from lib/credentials.py (gitignored).
    Copy lib/credentials.example.py to lib/credentials.py and fill in your values.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def load_commands(self):
        """Fetch both SharePoint lists, resolve lookups, and build the command cache."""
        headers = self._get_auth_headers()
        block_commands = self._load_block_commands(headers)
        self._commands = {}
        self._build_commands(headers, block_commands)
        print(f"SharePointCommandRepository: loaded {len(self._commands)} command entries.")
            # Print the loaded commands in the debug console
        for cmd_id, cmd_data in self._commands.items():
            print(f"Command ID: {cmd_id}")
            print(f"  Details: {cmd_data}")
            print("-" * 40)  # Separator for readability

    def get_step(self, block_cmd_id, limit_type):
        """Return the calculated step dict for (BlockCmdID, LimitType)."""
        key = (block_cmd_id, limit_type)
        if key not in self._commands:
            raise KeyError(
                f"No command found for BlockCmdID='{block_cmd_id}' LimitType='{limit_type}'"
            )
        return self._commands[key]

    # ── private helpers ──────────────────────────────────────────────────────────

    def _get_auth_headers(self):
        app = msal.ConfidentialClientApplication(
            config.SP_CLIENT_ID,
            client_credential=config.SP_CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/{config.SP_TENANT_ID}",
        )
        token = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        if "access_token" not in token:
            raise RuntimeError(f"Token acquisition failed: {token}")
        return {"Authorization": f"Bearer {token['access_token']}"}

    def _fetch_all_items(self, list_id, headers, select_fields=None):
        base = f"https://graph.microsoft.com/v1.0/sites/{config.SP_SITE_ID}/lists/{list_id}/items"
        if select_fields:
            url = f"{base}?$expand=fields($select={','.join(select_fields)})"
        else:
            url = f"{base}?$expand=fields"

        items = []
        next_url = url
        while next_url:
            r = requests.get(next_url, headers=headers)
            if r.status_code != 200:
                raise RuntimeError(
                    f"Error fetching list {list_id}: {r.status_code} – {r.text}"
                )
            data = r.json()
            items.extend(data.get("value", []))
            next_url = data.get("@odata.nextLink")
        return items

    def _load_block_commands(self, headers):
        items = self._fetch_all_items(config.SP_BLOCK_COMMANDS_LIST_ID, headers)
        return {
            str(item.get("id")).strip(): item.get("fields", {})
            for item in items
        }

    def _build_commands(self, headers, block_commands):
        items = self._fetch_all_items(
            config.SP_COMMAND_LIMITS_LIST_ID, headers,
            select_fields=_COMMAND_LIMITS_FIELDS,
        )
        for item in items:
            f = item.get("fields", {})
            lookup_id = str(f.get("LUBlockCommandTitleLookupId", "")).strip()
            if not lookup_id:
                continue
            source = block_commands.get(lookup_id)
            if not source:
                continue
            block_cmd_id = source.get("BlockCmdID")
            limit_type   = f.get("LimitType")
            if not block_cmd_id or not limit_type:
                continue
            self._commands[(block_cmd_id, limit_type)] = self._calculate_commands(f, source)

    def _calculate_commands(self, f, source):
        table      = int(source["Table"])
        block      = int(source["Block"])
        offset     = int(source["ByteOffset"])
        bytes_val  = int(source["Bytes"])
        meas_value = f["MeasValue"]
        format_txt = source["FormatTXT"]
        divisor    = float(source["DivisorTXT"])
        set_expected = str(source["SetExpected"])

        set_cmd  = command_set(
            MSG_TYPE_SET, COMMAND_ID, DEST_ADDR,
            table, block, offset, bytes_val,
            meas_value, format_txt, divisor,
        )
        read_cmd = command_read(
            MSG_TYPE_READ, COMMAND_ID, DEST_ADDR,
            table, block, offset, bytes_val,
        )
        read_exp = read_expected(
            MSG_TYPE_READ, COMMAND_ID, DEST_ADDR,
            table, block, offset, bytes_val,
            meas_value, format_txt, divisor,
        )

        return {
            "BlockCmdID":    source["BlockCmdID"],
            "LimitType":     f["LimitType"],
            "TeleField":     source.get("TeleField", ""),
            "CloudField":    source.get("CloudField", ""),
            "SetCommand":    set_cmd,
            "SetExpected":   set_expected,
            "ReadCommand":   read_cmd,
            "ReadExpected":  read_exp,
            "TeleExpected":  str(f.get("TeleExpected", "")),
            "CloudExpected": str(f.get("CloudExpected", "")),
        }
