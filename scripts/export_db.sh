#!/bin/bash
# Export Odoo database to backups/ folder
DB_NAME=${1:-iron_zone}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="backups/${DB_NAME}_${TIMESTAMP}.sql"

echo "Exporting database '$DB_NAME' to $OUTPUT ..."
docker exec iron_zone_db pg_dump -U odoo "$DB_NAME" > "$OUTPUT"
echo "Done: $OUTPUT"
