#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Script para ejecutar tests con Stagehand
.DESCRIPTION
    Ejecuta tests E2E del módulo de eventos con Stagehand
.PARAMETER Test
    Archivo de test a ejecutar (por defecto: todos)
.PARAMETER Headed
    Mostrar navegador durante tests
.PARAMETER Debug
    Ejecutar en modo debug
.PARAMETER Watch
    Ejecutar en modo watch (re-ejecutar al cambiar archivos)
.EXAMPLE
    .\run_stagehand_tests.ps1
    .\run_stagehand_tests.ps1 -Test events.test.js -Headed
    .\run_stagehand_tests.ps1 -Debug
#>

param(
    [string]$Test = $null,
    [switch]$Headed = $false,
    [switch]$Debug = $false,
    [switch]$Watch = $false,
    [string]$BaseURL = "http://localhost:8069",
    [string]$OdooUser = "admin",
    [string]$OdooPassword = "admin",
    [switch]$SkipServer = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🧪 Iron Zone - Stagehand Test Runner" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Verificar que npm está instalado
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npm no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar que node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
    npm install
}

# Verificar que stagehand está instalado
if (-not (Test-Path "node_modules/@stagehand/cli")) {
    Write-Host "📦 Instalando Stagehand..." -ForegroundColor Yellow
    npm install @stagehand/core @stagehand/cli --save-dev
}

# Configurar variables de entorno
$env:BASE_URL = $BaseURL
$env:ODOO_USER = $OdooUser
$env:ODOO_PASSWORD = $OdooPassword

if ($SkipServer) {
    $env:SKIP_SERVER = "true"
}

# Construir comando
$cmd = "stagehand"

if ($Test) {
    $testPath = "tests/e2e/$Test"
    $cmd += " --test $testPath"
} else {
    $cmd += " --test tests/e2e/*.test.js"
}

if ($Headed) {
    $cmd += " --headed"
}

if ($Debug) {
    $cmd += " --debug"
}

if ($Watch) {
    $cmd += " --watch"
}

Write-Host "🚀 Ejecutando: $cmd" -ForegroundColor Green
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  BASE_URL: $BaseURL" -ForegroundColor Gray
Write-Host "  ODOO_USER: $OdooUser" -ForegroundColor Gray
Write-Host "  HEADLESS: $(if ($Headed) { "false" } else { "true" })" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray

# Ejecutar comando
npx $cmd

$exitCode = $LASTEXITCODE
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "✅ Tests completados exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Tests fallaron con código de salida: $exitCode" -ForegroundColor Red
}

exit $exitCode
