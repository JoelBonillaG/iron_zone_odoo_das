#!/usr/bin/env bash

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Valores por defecto
TEST_FILE=""
HEADED=false
DEBUG=false
WATCH=false
BASE_URL="${BASE_URL:-http://localhost:8069}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASSWORD="${ODOO_PASSWORD:-admin}"
SKIP_SERVER=false

# Ayuda
show_help() {
    cat << EOF
Uso: $0 [opciones]

Opciones:
    -t, --test FILE       Archivo de test a ejecutar (ej: events.test.js)
    -h, --headed          Mostrar navegador durante tests
    -d, --debug           Ejecutar en modo debug
    -w, --watch           Ejecutar en modo watch
    --base-url URL        URL base de Odoo (por defecto: http://localhost:8069)
    --user USER           Usuario de Odoo (por defecto: admin)
    --password PASS       Contraseña de Odoo (por defecto: admin)
    --skip-server         Omitir inicio del servidor
    --help                Mostrar esta ayuda

Ejemplos:
    $0
    $0 --test events.test.js --headed
    $0 --debug
    $0 --watch
EOF
}

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--test)
            TEST_FILE="$2"
            shift 2
            ;;
        -h|--headed)
            HEADED=true
            shift
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        --base-url)
            BASE_URL="$2"
            shift 2
            ;;
        --user)
            ODOO_USER="$2"
            shift 2
            ;;
        --password)
            ODOO_PASSWORD="$2"
            shift 2
            ;;
        --skip-server)
            SKIP_SERVER=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

echo -e "${CYAN}🧪 Iron Zone - Stagehand Test Runner${NC}"
echo -e "${CYAN}$(printf '=%.0s' {1..50})${NC}"

# Verificar que npm está instalado
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm no está instalado${NC}"
    exit 1
fi

# Verificar que node_modules existe
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    npm install
fi

# Verificar que stagehand está instalado
if [ ! -d "node_modules/@stagehand/cli" ]; then
    echo -e "${YELLOW}📦 Instalando Stagehand...${NC}"
    npm install @stagehand/core @stagehand/cli --save-dev
fi

# Exportar variables de entorno
export BASE_URL
export ODOO_USER
export ODOO_PASSWORD

if [ "$SKIP_SERVER" = true ]; then
    export SKIP_SERVER=true
fi

# Construir comando
CMD="stagehand"

if [ -n "$TEST_FILE" ]; then
    CMD="$CMD --test tests/e2e/$TEST_FILE"
else
    CMD="$CMD --test tests/e2e/*.test.js"
fi

if [ "$HEADED" = true ]; then
    CMD="$CMD --headed"
fi

if [ "$DEBUG" = true ]; then
    CMD="$CMD --debug"
fi

if [ "$WATCH" = true ]; then
    CMD="$CMD --watch"
fi

echo -e "${GREEN}🚀 Ejecutando: $CMD${NC}"
echo -e "${CYAN}Configuration:${NC}"
echo -e "  BASE_URL: ${BASE_URL}"
echo -e "  ODOO_USER: ${ODOO_USER}"
echo -e "  HEADLESS: $([ "$HEADED" = true ] && echo "false" || echo "true")"
echo ""

# Ejecutar comando
npx $CMD

EXIT_CODE=$?

echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tests completados exitosamente${NC}"
else
    echo -e "${RED}❌ Tests fallaron con código de salida: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
