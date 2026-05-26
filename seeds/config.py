import os
import xmlrpc.client
from pathlib import Path


def load_env_file():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return {}

    values = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        values[key] = value
    return values


def env_value(*names, default):
    for name in names:
        value = os.getenv(name) if name.startswith("ODOO_") else None
        if value:
            return value
        value = ENV_FILE_VALUES.get(name)
        if value:
            return value
    return default


ENV_FILE_VALUES = load_env_file()

URL      = env_value("ODOO_URL", "URL", default="http://localhost:8069")
DB       = env_value("ODOO_DB", "DB_NAME", "DB", default="iron_zone")
USERNAME = env_value("ODOO_USERNAME", "ODOO_USER", "USERNAME", default="admin@ironzone.com")
PASSWORD = env_value("ODOO_PASSWORD", "PASSWORD", default="admin123")

def resolve_credentials():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    candidates = [
        (USERNAME, PASSWORD),
        ("admin", "admin"),
        ("admin@ironzone.com", "admin123"),
    ]
    seen = set()
    for login, password in candidates:
        key = (login, password)
        if key in seen:
            continue
        seen.add(key)
        uid = common.authenticate(DB, login, password, {})
        if uid:
            return uid, login, password
    return False, USERNAME, PASSWORD


UID, USERNAME, PASSWORD = resolve_credentials()

def connect():
    if not UID:
        raise Exception("Auth failed. Verify USERNAME/PASSWORD in seeds/config.py")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    return UID, models

def create(uid, models, model, vals_list):
    return models.execute_kw(DB, uid, PASSWORD, model, "create", [vals_list])

def search_read(uid, models, model, domain, fields):
    return models.execute_kw(DB, uid, PASSWORD, model, "search_read", [domain], {"fields": fields})
