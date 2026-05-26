# ══════════════════════════════════════════════════════════════════
# EJECUTOR DE PRUEBAS DE EMAIL - IRON ZONE GYM
# ══════════════════════════════════════════════════════════════════
# Ejecuta este script desde tu terminal de PowerShell:
#
# .\scripts\run_test.ps1
# ══════════════════════════════════════════════════════════════════

# Resolver rutas relativas dinámicamente basadas en la ubicación de este script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$envPath = Join-Path $projectRoot ".env"
$scriptToRun = Join-Path $scriptDir "test_marketing_emails.py"

# 1. Intentar cargar el TEST_EMAIL desde el archivo .env del root
$testEmail = "ejemplo@ironzone.com"
if (Test-Path $envPath) {
    $envLines = Get-Content $envPath
    foreach ($line in $envLines) {
        if ($line -match "^TEST_EMAIL=(.*)") {
            $testEmail = $Matches[1].Trim()
            break
        }
    }
}

# 2. Informar al desarrollador
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host "   IRON ZONE - EJECUTANDO PRUEBA DE CORREOS AUTOMÁTICOS" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host "[*] Destinatario de Pruebas: $testEmail" -ForegroundColor Cyan
Write-Host "[*] Leyendo script desde: $scriptToRun" -ForegroundColor Cyan
Write-Host "[*] Enviando al contenedor Docker 'iron_zone_odoo'..." -ForegroundColor Cyan
Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray

# 3. Lanzar la ejecución dentro de Odoo
Get-Content $scriptToRun | docker exec -i -e TEST_EMAIL="$testEmail" iron_zone_odoo odoo shell -c /etc/odoo/odoo.conf -d iron_zone --no-http --stop-after-init

Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "[+] Ejecución finalizada con éxito." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Yellow
