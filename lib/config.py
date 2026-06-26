import os

_HERE = os.path.dirname(os.path.abspath(__file__))      # lib/
_ROOT = os.path.dirname(_HERE)                          # RobotFramework/
_PROJECT = os.path.dirname(_ROOT)                       # End2EndTestingV2/


def get_env(name: str) -> str:
    """
    Read a required environment variable.
    Raises a clear exception if it is missing.
    """
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise RuntimeError(
            f"Required environment variable '{name}' is not set."
        )

    return value


# ── AWS IoT ───────────────────────────────────────────────────────────────────

ENDPOINT = get_env("AWS_ENDPOINT")

CERT_FILE = os.path.join(_HERE, "certs", "CST-E2E-1.cert.pem")
KEY_FILE  = os.path.join(_HERE, "certs", "CST-E2E-1.private.key")
CA_FILE   = os.path.join(_HERE, "certs", "AmazonRootCA1.pem")


# ── SharePoint / Microsoft Graph ─────────────────────────────────────────────

SP_TENANT_ID = get_env("SP_TENANT_ID")
SP_CLIENT_ID = get_env("SP_CLIENT_ID")
SP_CLIENT_SECRET = get_env("SP_CLIENT_SECRET")
SP_SITE_ID = get_env("SP_SITE_ID")
SP_COMMAND_LIMITS_LIST_ID = get_env("SP_COMMAND_LIMITS_LIST_ID")
SP_BLOCK_COMMANDS_LIST_ID = get_env("SP_BLOCK_COMMANDS_LIST_ID")


# ── Paths ─────────────────────────────────────────────────────────────────────

BLOB_ROOT = os.path.join(_PROJECT, "RobotFramework", "Blobstorage")
