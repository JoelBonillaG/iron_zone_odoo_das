import os
import xml.etree.ElementTree as ET
import xmlrpc.client
from pathlib import Path

import base64
from config import URL, DB, USERNAME, PASSWORD


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def load_env_file_if_present() -> None:
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


def read_template_fields(xml_path: Path) -> dict[str, dict[str, str]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    templates: dict[str, dict[str, str]] = {}

    for record in root.findall(".//record[@model='mail.template']"):
        record_id = record.get("id") or ""
        if record_id not in {
            "mail_template_welcome",
            "auth_signup.mail_template_user_signup_account_created",
            "mail_template_birthday",
        }:
            continue

        values: dict[str, str] = {}
        for field in record.findall("field"):
            field_name = field.get("name")
            if field_name and field.text is not None:
                values[field_name] = field.text
        templates[record_id] = values

    return templates


def resolve_template_id(models, uid, record_id: str):
    if record_id == "auth_signup.mail_template_user_signup_account_created":
        matches = models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "ir.model.data",
            "search_read",
            [[("model", "=", "mail.template"), ("name", "=", "mail_template_user_signup_account_created")]],
            {"fields": ["res_id", "module", "name"], "limit": 5},
        )
        if matches:
            return matches[0]["res_id"]
        return None

    matches = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "ir.model.data",
        "search_read",
        [[("module", "=", "iz_website"), ("name", "=", record_id), ("model", "=", "mail.template")]],
        {"fields": ["res_id"], "limit": 1},
    )
    if matches:
        return matches[0]["res_id"]
    return None


load_env_file_if_present()

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    raise RuntimeError("Authentication failed. Check seeds/config.py credentials.")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
repo_root = Path(__file__).resolve().parents[1]
xml_path = repo_root / "addons" / "iz_website" / "data" / "email_templates.xml"
template_fields = read_template_fields(xml_path)

if not template_fields:
    raise RuntimeError(f"No mail.template records found in {xml_path}")

# First, sync templates
for record_id, values in template_fields.items():
    template_id = resolve_template_id(models, uid, record_id)
    if not template_id:
        print(f"Template not found, skipping: {record_id}")
        continue

    models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "mail.template",
        "write",
        [[template_id], values],
    )
    print(f"Template synchronized: {record_id}")

# Then, ensure company.logo is set from a static file if not present
def find_static_logo(root: Path) -> Path | None:
    candidates = [
        root / "addons" / "iz_website" / "static" / "src" / "img" / "IronZone.png",
        root / "seeds" / "IronZone.png",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

logo_path = find_static_logo(repo_root)
if not logo_path:
    print("No static logo file found; skipping company.logo update.")
else:
    # Check existing company logo
    companies = models.execute_kw(DB, uid, PASSWORD, 'res.company', 'search_read', [[['id', '!=', False]]], {'fields': ['id', 'logo'], 'limit': 5})
    if not companies:
        print('No companies found to update logo; skipping.')
    else:
        # Use first company (typical single-company dev env)
        comp = companies[0]
        comp_id = comp['id']
        existing = comp.get('logo')
        if existing:
            print(f'Company {comp_id} already has a logo; skipping update.')
        else:
            print(f'Setting company {comp_id} logo from {logo_path}')
            img_bytes = logo_path.read_bytes()
            b64 = base64.b64encode(img_bytes).decode('ascii')
            # write to 'logo' field which is used as data URI source in templates
            models.execute_kw(DB, uid, PASSWORD, 'res.company', 'write', [[comp_id], {'logo': b64}])
            print('Company logo updated (field: logo)')
