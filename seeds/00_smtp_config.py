import os
import xmlrpc.client
from pathlib import Path
from config import URL, DB, USERNAME, PASSWORD


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def load_env_file_if_present() -> None:
    """Best-effort .env loader for local execution (esp. PowerShell/Windows).

    Only sets variables that are not already present in the environment.
    """

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file_if_present()


SMTP_HOST = get_env("SMTP_HOST")
SMTP_PORT = int(get_env("SMTP_PORT", "587"))
SMTP_USER = get_env("SMTP_USER")
SMTP_PASSWORD = get_env("SMTP_PASSWORD")
SMTP_FROM = get_env("SMTP_FROM", SMTP_USER)
SMTP_ENCRYPTION = get_env("SMTP_ENCRYPTION", "starttls")

print(
    "Configuring SMTP...",
    f"URL={URL}",
    f"DB={DB}",
    f"HOST={SMTP_HOST}",
    f"PORT={SMTP_PORT}",
    f"USER={SMTP_USER}",
    f"FROM={SMTP_FROM}",
    f"ENCRYPTION={SMTP_ENCRYPTION}",
    f"PASSWORD_SET={bool(SMTP_PASSWORD)}",
)

if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
    raise RuntimeError(
        "Missing SMTP configuration. Check SMTP_HOST, SMTP_USER and SMTP_PASSWORD in .env"
    )

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})

if not uid:
    raise RuntimeError("Authentication failed. Check seeds/config.py credentials.")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

existing_ids = models.execute_kw(
    DB,
    uid,
    PASSWORD,
    "ir.mail_server",
    "search",
    [[("smtp_host", "=", SMTP_HOST), ("smtp_user", "=", SMTP_USER)]],
    {"limit": 1},
)

values = {
    "name": "Iron Zone SMTP",
    "smtp_host": SMTP_HOST,
    "smtp_port": SMTP_PORT,
    "smtp_user": SMTP_USER,
    "smtp_pass": SMTP_PASSWORD,
    "smtp_encryption": SMTP_ENCRYPTION,
    "from_filter": SMTP_FROM,
    "sequence": 1,
    "active": True,
}

if existing_ids:
    models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "ir.mail_server",
        "write",
        [existing_ids, values],
    )
    print("SMTP server updated successfully.")
else:
    models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "ir.mail_server",
        "create",
        [values],
    )
    print("SMTP server created successfully.")
    existing_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "ir.mail_server",
        "search",
        [[("smtp_host", "=", SMTP_HOST), ("smtp_user", "=", SMTP_USER)]],
        {"limit": 1},
    )

configured_id = existing_ids[0]
other_active_ids = models.execute_kw(
    DB,
    uid,
    PASSWORD,
    "ir.mail_server",
    "search",
    [[("id", "!=", configured_id), ("active", "=", True)]],
)
if other_active_ids:
    models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "ir.mail_server",
        "write",
        [other_active_ids, {"active": False}],
    )
    print(f"Disabled {len(other_active_ids)} old SMTP server(s).")
