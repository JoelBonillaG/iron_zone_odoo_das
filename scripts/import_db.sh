#!/bin/bash
# Import a .sql backup into the Odoo database
SQL_FILE=${1}
DB_NAME=${2:-iron_zone}

if [ -z "$SQL_FILE" ]; then
  echo "Usage: ./scripts/import_db.sh <file.sql> [db_name]"
  exit 1
fi

echo "Creating database '$DB_NAME' if not exists..."
docker exec iron_zone_db psql -U odoo -c "CREATE DATABASE $DB_NAME OWNER odoo;" 2>/dev/null || true

echo "Importing $SQL_FILE into '$DB_NAME' ..."
docker exec -i iron_zone_db psql -U odoo "$DB_NAME" < "$SQL_FILE"
echo "Done."
