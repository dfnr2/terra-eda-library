# Setup script for Terra EDA Library
# Generates terra.kicad_dbl with absolute path for local KiCad use

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Terra EDA Library Setup" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Library path: $ScriptDir"
Write-Host ""

# Generate terra.kicad_dbl from template
$templatePath = Join-Path $ScriptDir "terra.kicad_dbl.template"
$outputPath = Join-Path $ScriptDir "terra.kicad_dbl"

if (Test-Path $templatePath) {
    Write-Host "Generating terra.kicad_dbl with absolute path..."

    # Read template and replace placeholder with actual path
    $content = Get-Content $templatePath -Raw
    # Convert Windows path to forward slashes for consistency
    $libraryPath = $ScriptDir -replace '\\', '/'
    $content = $content -replace '__TERRA_PATH__', $libraryPath

    # Write output
    Set-Content -Path $outputPath -Value $content -NoNewline
    Write-Host "Created terra.kicad_dbl" -ForegroundColor Green
} else {
    Write-Host "ERROR: Template file not found: terra.kicad_dbl.template" -ForegroundColor Red
    exit 1
}

# Build database if needed
$dbPath = Join-Path $ScriptDir "db\terra.db"
if (-not (Test-Path $dbPath)) {
    Write-Host ""
    Write-Host "Building database..."

    # Check if make is available
    $hasMake = $null -ne (Get-Command make -ErrorAction SilentlyContinue)

    if ($hasMake) {
        make -C $ScriptDir all
    } else {
        # Use build.ps1 instead
        & (Join-Path $ScriptDir "build.ps1")
    }

    Write-Host "Database built" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To use this library in KiCad:"
Write-Host "1. Set environment variable in KiCad:"
Write-Host "   Preferences -> Configure Paths"
Write-Host "   Name: TERRA_EDA_LIB"
Write-Host "   Path: $ScriptDir"
Write-Host ""
Write-Host "2. Add symbol library:"
Write-Host "   Preferences -> Manage Symbol Libraries"
Write-Host "   Path: `${TERRA_EDA_LIB}/terra_sym.kicad_sym"
Write-Host "   Nickname: terra_sym"
Write-Host ""
Write-Host "3. Add database library:"
Write-Host "   In your project, type the path:"
Write-Host "   `${TERRA_EDA_LIB}/terra.kicad_dbl"
Write-Host "   (File may appear grayed out in browser, just type the path directly)"
Write-Host ""
