#!/usr/bin/env bash
set -euo pipefail

export MSYS_NO_PATHCONV=1

DB_NAME="${DB_NAME:-iron_zone}"
ODOO_CONTAINER="${ODOO_CONTAINER:-iron_zone_odoo}"
DB_CONTAINER="${DB_CONTAINER:-iron_zone_db}"
ODOO_CONFIG="/etc/odoo/odoo.conf"

DEFAULT_MODULES=(
  # Odoo base apps
  website
  website_sale
  website_sale_stock
  account
  account_payment
  account_edi
  l10n_ec
  website_payment
  payment_demo
  payment_custom
  hr
  mass_mailing
  appointment
  sale_management
  stock
  purchase
  event
  website_event
  calendar

  # Iron Zone custom modules
  iz_website
  iz_inventory
  iz_backend_theme
  iz_subscription

  # Ecuador electronic invoicing custom modules
  l10n_ec_base
  l10n_ec_edi
  l10n_ec_sri
  l10n_ec_withholding
  l10n_ec_reports
)

MODULES="${MODULES:-$(IFS=,; echo "${DEFAULT_MODULES[*]}")}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! docker inspect "$ODOO_CONTAINER" >/dev/null 2>&1; then
  echo "Odoo container '$ODOO_CONTAINER' was not found. Start it with: docker compose up -d"
  exit 1
fi

if ! docker inspect -f '{{.State.Running}}' "$DB_CONTAINER" >/dev/null 2>&1; then
  echo "Database container '$DB_CONTAINER' is not running. Start it with: docker compose up -d"
  exit 1
fi

ODOO_IMAGE="$(docker inspect -f '{{.Config.Image}}' "$ODOO_CONTAINER")"
DB_NETWORK="$(docker inspect -f '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' "$DB_CONTAINER" | head -n 1)"

if [ -z "$ODOO_IMAGE" ] || [ -z "$DB_NETWORK" ]; then
  echo "Could not detect Odoo image or Docker network."
  exit 1
fi

echo "Installing or updating base apps into database: $DB_NAME"

if [ "$(docker inspect -f '{{.State.Running}}' "$ODOO_CONTAINER")" = "true" ]; then
  echo "Stopping Odoo to release database locks..."
  docker stop "$ODOO_CONTAINER" >/dev/null
fi

start_odoo() {
  docker start "$ODOO_CONTAINER" >/dev/null 2>&1 || true
}

trap start_odoo EXIT

docker run --rm \
  --network "$DB_NETWORK" \
  --volumes-from "$ODOO_CONTAINER" \
  "$ODOO_IMAGE" \
  odoo \
    -c "$ODOO_CONFIG" \
    -d "$DB_NAME" \
    -i "$MODULES" \
    -u "$MODULES" \
    --without-demo=all \
    --log-level=warn \
    --logfile=/dev/stdout \
    --stop-after-init

echo "Starting Odoo..."
start_odoo
trap - EXIT

echo "Apps installed successfully."
