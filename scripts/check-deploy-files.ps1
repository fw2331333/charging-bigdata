# Verify files required for GitHub / server Docker deploy
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Required = @(
    "docker-compose.yml",
    ".env.docker.example",
    "docker\README.md",
    "docker\mysql\03-seed.sh",
    "sql\schema.sql",
    "sql\ads_schema.sql",
    "sql\auth_schema.sql",
    "sql\view_config_schema.sql",
    "sql\migrations\004_email_verification.sql",
    "sql\migrations\005_profile_otp.sql",
    "sql\seed\charging_bigdata_data.sql",
    "sql\seed\auth_users.sql",
    "backend\Dockerfile",
    "backend\requirements.txt",
    "backend\main.py",
    "backend\app\main.py",
    "frontend\Dockerfile",
    "frontend\nginx.conf",
    "frontend\package.json",
    "frontend\package-lock.json",
    "frontend\src\main.ts",
    "analytics\output\models\.gitkeep"
)

$Optional = @(
    "docker-compose.datart.yml",
    "analytics\output\models\metrics.json",
    "analytics\output\models\performance_report.json",
    "analytics\output\models\fee_model.pkl",
    "analytics\output\models\duration_model.pkl",
    "analytics\output\models\platform_model.pkl",
    "analytics\output\models\soc_model.pkl"
)

$Forbidden = @(".env", "backend\.env", "config\pipeline.env")

$missing = $false
foreach ($f in $Required) {
    if (-not (Test-Path $f)) {
        Write-Host "[MISSING] $f" -ForegroundColor Red
        $missing = $true
    }
}

Write-Host ""
Write-Host "Optional (predict / datart):"
foreach ($f in $Optional) {
    if (Test-Path $f) { Write-Host "  [OK] $f" -ForegroundColor Green }
    else { Write-Host "  [--] $f" }
}

Write-Host ""
Write-Host "Secrets (must stay gitignored):"
foreach ($f in $Forbidden) {
    if (Test-Path $f) {
        git check-ignore -q $f 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-Host "  [ignored] $f" }
        else {
            Write-Host "  [WARN] $f exists but not gitignored" -ForegroundColor Yellow
            $missing = $true
        }
    }
}

Write-Host ""
if (-not $missing) {
    Write-Host "Deploy file check passed." -ForegroundColor Green
    exit 0
}
Write-Host "See docs/deploy-github-manifest.md" -ForegroundColor Red
exit 1
