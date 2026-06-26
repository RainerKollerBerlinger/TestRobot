import os
import sys

_HERE    = os.path.dirname(os.path.abspath(__file__))  # lib/
_ROOT    = os.path.dirname(_HERE)                      # RobotFramework/
_PROJECT = os.path.dirname(_ROOT)                      # End2EndTestingV2/

# Load secrets — copy lib/credentials.example.py to lib/credentials.py and fill in values
sys.path.insert(0, _HERE)
try:
    import credentials as _c
except ModuleNotFoundError:
    raise FileNotFoundError(
        "lib/credentials.py not found. "
        "Copy lib/credentials.example.py to lib/credentials.py and fill in your values."
    )

# ── AWS IoT ───────────────────────────────────────────────────────────────────
ENDPOINT  = _c.AWS_ENDPOINT
CERT_FILE = os.path.join(_HERE, "certs", "CST-E2E-1.cert.pem")
KEY_FILE  = os.path.join(_HERE, "certs", "CST-E2E-1.private.key")
CA_FILE   = os.path.join(_HERE, "certs", "AmazonRootCA1.pem")

# ── SharePoint / Microsoft Graph ─────────────────────────────────────────────
SP_TENANT_ID              = _c.SP_TENANT_ID
SP_CLIENT_ID              = _c.SP_CLIENT_ID
SP_CLIENT_SECRET          = _c.SP_CLIENT_SECRET
SP_SITE_ID                = _c.SP_SITE_ID
SP_COMMAND_LIMITS_LIST_ID = _c.SP_COMMAND_LIMITS_LIST_ID
SP_BLOCK_COMMANDS_LIST_ID = _c.SP_BLOCK_COMMANDS_LIST_ID

# ── Paths ─────────────────────────────────────────────────────────────────────
BLOB_ROOT = os.path.join(_PROJECT, "RobotFramework", "Blobstorage")
