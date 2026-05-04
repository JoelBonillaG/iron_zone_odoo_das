param(
    [string]$DbName = $(if ($env:DB_NAME) { $env:DB_NAME } else { "iron_zone" }),
    [string]$OdooContainer = $(if ($env:ODOO_CONTAINER) { $env:ODOO_CONTAINER } else { "iron_zone_odoo" }),
    [string]$DbContainer = $(if ($env:DB_CONTAINER) { $env:DB_CONTAINER } else { "iron_zone_db" }),
    [string]$DbUser = $(if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "odoo" })
)

$ErrorActionPreference = "Stop"

$Modules = "website,website_sale,website_sale_stock,account,account_payment,website_payment,payment_demo,payment_custom,hr,mass_mailing,appointment,sale_management,stock,iz_website,iz_inventory,iz_backend_theme"
$OdooConfig = "/etc/odoo/odoo.conf"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$SeedsDir = Join-Path $RepoRoot "seeds"

function Invoke-Checked {
    param([string[]]$Command)

    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $($Command -join ' ')"
    }
}

Write-Host "Resetting local Odoo database '$DbName'..."

docker inspect $DbContainer *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Database container '$DbContainer' was not found. Run: docker compose up -d"
}

docker inspect $OdooContainer *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Odoo container '$OdooContainer' was not found. Run: docker compose up -d"
}

Write-Host "Stopping Odoo to release database connections..."
docker stop $OdooContainer | Out-Null

try {
    Write-Host "Dropping and recreating PostgreSQL database..."
    Invoke-Checked @("docker", "exec", $DbContainer, "psql", "-U", $DbUser, "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-c", "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DbName';")
    Invoke-Checked @("docker", "exec", $DbContainer, "dropdb", "-U", $DbUser, "--if-exists", $DbName)
    Invoke-Checked @("docker", "exec", $DbContainer, "createdb", "-U", $DbUser, $DbName)

    Write-Host "Starting Odoo container..."
    docker start $OdooContainer | Out-Null
    Start-Sleep -Seconds 5

    Write-Host "Installing project modules into the empty database..."
    Invoke-Checked @(
        "docker", "exec", "-i", $OdooContainer,
        "odoo", "-c", $OdooConfig,
        "-d", $DbName,
        "-i", $Modules,
        "-u", $Modules,
        "--without-demo=all",
        "--stop-after-init"
    )

    Write-Host "Restarting Odoo after module installation..."
    docker restart $OdooContainer | Out-Null
    Start-Sleep -Seconds 8

    Write-Host "Configuring default admin credentials for seeds..."
    $AdminScript = @"
admin = env.ref('base.user_admin')
admin.write({
    'name': 'Administrador Iron Zone',
    'login': 'admin@ironzone.com',
    'email': 'admin@ironzone.com',
    'password': 'admin123',
})
env.cr.commit()
print('Admin user reset:', admin.login)
"@
    $AdminScript | docker exec -i $OdooContainer odoo shell -c $OdooConfig -d $DbName
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to configure admin credentials."
    }

    Write-Host "Running seeds from scratch..."
    Push-Location $RepoRoot
    try {
        Invoke-Checked @("python", (Join-Path $SeedsDir "00_company_config.py"))
        Invoke-Checked @("python", (Join-Path $SeedsDir "00_smtp_config.py"))

        Get-ChildItem -Path $SeedsDir -Filter "*.py" |
            Sort-Object Name |
            Where-Object { $_.Name -match "^\d" -and $_.Name -notin @("00_company_config.py", "00_smtp_config.py") } |
            ForEach-Object {
                Write-Host "Running $($_.Name)..."
                Invoke-Checked @("python", $_.FullName)
            }
    }
    finally {
        Pop-Location
    }

    Write-Host "Database reset completed: $DbName"
}
catch {
    Write-Host "Reset failed. Ensuring Odoo container is running again..."
    docker start $OdooContainer *> $null
    throw
}
