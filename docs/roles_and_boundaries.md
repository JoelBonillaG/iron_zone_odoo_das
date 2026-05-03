# Roles and boundaries

Recommended functional split for this project:

- Frontend / Website: owns public pages, branding, content sections and shop UX.
- Catalog / Sales: owns products, categories, pricing, publication rules and commercial flows.
- Inventory / Operations: owns stock levels, replenishment, warehouse rules and sell-out policies.

Suggested Odoo app ownership:

- `iz_website`: homepage, about page, footer, frontend assets and visual consistency.
- `iz_inventory`: stock-related business conventions and future inventory-specific rules.
- Standard Odoo modules: `website_sale`, `website_sale_stock`, `sale_management`, `stock`.

Recommended group assignment:

- Website editor: content and layout only.
- Catalog manager: products, categories, prices and publication.
- Inventory manager: stock adjustments, receipts, deliveries and replenishment.
- Administrator: cross-module configuration and security.

Backend rule adopted in the seeds:

- Storable products are created with `allow_out_of_stock_order = False` when the field is available.
- Physical products get an availability threshold and an out-of-stock message for the website.
- Product/category seeding is idempotent so rerunning the seed updates data instead of duplicating it.
