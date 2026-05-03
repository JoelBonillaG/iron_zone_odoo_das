import base64
from pathlib import Path
import xmlrpc.client
from typing import Optional

from config import URL, DB, USERNAME, PASSWORD


def load_logo_base64() -> Optional[str]:
    """Load the Iron Zone logo from the seeds folder and return it as base64.

    Expected filename: IronZone.png
    """
    seeds_dir = Path(__file__).resolve().parent
    logo_path = seeds_dir / "IronZone.png"
    if not logo_path.exists():
        return None

    with logo_path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    raise RuntimeError("Authentication failed. Check seeds/config.py credentials.")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

company_ids = models.execute_kw(
    DB,
    uid,
    PASSWORD,
    "res.company",
    "search",
    [[("name", "!=", False)]],
    {"limit": 1},
)

if not company_ids:
    raise RuntimeError("No company found in Odoo. Create the database first via the web wizard.")

company_id = company_ids[0]

country_ids = models.execute_kw(
    DB,
    uid,
    PASSWORD,
    "res.country",
    "search",
    [[("code", "=", "EC")]],
    {"limit": 1},
)

currency_ids = models.execute_kw(
    DB,
    uid,
    PASSWORD,
    "res.currency",
    "search",
    [[("name", "=", "USD")]],
    {"limit": 1},
)

values = {
    "name": "Iron Zone",
    "email": "contacto@ironzone.ec",
    "phone": "+593 3 282 4450",
    "street": "Av. Cevallos y Montalvo 245",
    "city": "Ambato",
    "website": "https://www.ironzone.ec",
}
if country_ids:
    values["country_id"] = country_ids[0]

if currency_ids:
    values["currency_id"] = currency_ids[0]
else:
    print("Warning: USD currency not found. Company currency was not updated.")

logo_base64 = load_logo_base64()
if logo_base64:
    values["logo"] = logo_base64
else:
    print("Warning: logo file not found. Place 'seeds/IronZone.png' to set the company logo.")

models.execute_kw(DB, uid, PASSWORD, "res.company", "write", [[company_id], values])

# Also update the Website record to match
website_ids = models.execute_kw(DB, uid, PASSWORD, "website", "search", [[]])
if website_ids:
    website_vals = {
        "name": "Iron Zone",
    }
    if logo_base64:
        website_vals["logo"] = logo_base64
    
    models.execute_kw(DB, uid, PASSWORD, "website", "write", [website_ids, website_vals])
    print(f"Website(s) updated: {len(website_ids)}")

print("Company configured successfully: Iron Zone")
