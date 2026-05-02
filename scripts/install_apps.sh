#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${DB_NAME:-iron_zone}"
ODOO_CONTAINER="${ODOO_CONTAINER:-iron_zone_odoo}"
MODULES="${MODULES:-website,website_sale,account,hr,mass_mailing,appointment,sale_management,stock}"
ODOO_CONFIG="/etc/odoo/odoo.conf"

if ! docker inspect -f '{{.State.Running}}' "$ODOO_CONTAINER" >/dev/null 2>&1; then
  echo "Odoo container '$ODOO_CONTAINER' is not running. Start it with: docker compose up -d"
  exit 1
fi

if ! docker exec "$ODOO_CONTAINER" test -f "$ODOO_CONFIG"; then
  echo "Odoo config not found at $ODOO_CONFIG inside the container."
  exit 1
fi

echo "Installing base apps into database: $DB_NAME"

docker exec -i "$ODOO_CONTAINER" odoo \
  -c "$ODOO_CONFIG" \
  -d "$DB_NAME" \
  -i "$MODULES" \
  --without-demo=all \
  --stop-after-init

echo "Restarting Odoo..."
docker restart "$ODOO_CONTAINER"

echo "Apps installed successfully."