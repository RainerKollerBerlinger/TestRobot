import os

_HERE = os.path.dirname(os.path.abspath(__file__))      # lib/
_ROOT = os.path.dirname(_HERE)                          # RobotFramework/
_PROJECT = os.path.dirname(_ROOT)                       # End2EndTestingV2/


def get_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise RuntimeError(
            f"Required environment variable '{name}' is not set."
        )

    return value.strip()


def get_hostname_env(name: str) -> str:
    value = get_env(name)

    # Remove accidental quotes
    value = value.strip('"').strip("'")

    # Common mistake: storing a URL instead of hostname
    if "://" in value:
        raise RuntimeError(
            f"Environment variable '{name}' must be a hostname only, "
            f"not a URL. Remove protocol prefix like https:// or mqtts://."
        )

    # Common mistake: storing host:port
    if ":" in value:
        raise RuntimeError(
            f"Environment variable '{name}' must not include a port. "
            f"Use hostname only, without :8883."
        )

    # Common mistake: storing path
    if "/" in value:
        raise RuntimeError(
            f"Environment variable '{name}' must not include a path. "
            f"Use hostname only."
        )

    return value


# ── AWS IoT ───────────────────────────────────────────────────────────────────

ENDPOINT = get_hostname_env("AWS_ENDPOINT")

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
