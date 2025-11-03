# Build Terra EDA Library databases from SQL
# Alternative to 'make' for Windows systems without make installed

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Building Terra EDA Library databases..." -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Create db directory if needed
if (-not (Test-Path "db")) {
    New-Item -ItemType Directory -Path "db" | Out-Null
}

# Check if sqlite3 is available
try {
    $null = Get-Command sqlite3 -ErrorAction Stop
} catch {
    Write-Host "ERROR: sqlite3 not found in PATH" -ForegroundColor Red
    Write-Host "Please install SQLite: https://www.sqlite.org/download.html" -ForegroundColor Yellow
    exit 1
}

# Build all databases from SQL files
$sqlFiles = Get-ChildItem -Path "db\*.sql" -ErrorAction SilentlyContinue

if ($sqlFiles.Count -eq 0) {
    Write-Host "No SQL files found in db/ directory" -ForegroundColor Yellow
    exit 0
}

foreach ($sqlFile in $sqlFiles) {
    $dbFile = $sqlFile.FullName -replace '\.sql$', '.db'
    Write-Host "Building: $dbFile"

    # Remove existing database
    if (Test-Path $dbFile) {
        Remove-Item $dbFile -Force
    }

    # Build database from SQL
    Get-Content $sqlFile | sqlite3 $dbFile
    Write-Host "  Done" -ForegroundColor Green
}

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Database files:"

$dbFiles = Get-ChildItem -Path "db\*.db" -ErrorAction SilentlyContinue
foreach ($dbFile in $dbFiles) {
    $count = sqlite3 $dbFile.FullName "SELECT COUNT(*) FROM symbols" 2>$null
    if (-not $count) { $count = 0 }
    $size = "{0:N2} KB" -f ($dbFile.Length / 1KB)
    Write-Host "  $($dbFile.FullName) ($count components, $size)"
}
