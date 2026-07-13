# Import MySQL seed for Web demo (no Hadoop required)
# Usage: powershell -ExecutionPolicy Bypass -File scripts/import_web_demo.ps1 -Password 123456
param(
    [string]$Mysql = "mysql",
    [string]$DbHost = "127.0.0.1",
    [int]$Port = 3306,
    [string]$User = "root",
    [string]$Password = "123456",
    [string]$Database = "charging_bigdata"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Invoke-MysqlFile([string]$File, [switch]$SelectDb) {
    if (-not (Test-Path $File)) { throw "Missing file: $File" }
    Write-Host "==> $File"
    $args = @("-h", $DbHost, "-P", $Port, "-u", $User, "-p$Password", "--default-character-set=utf8mb4")
    if ($SelectDb) { $args += $Database }
    Get-Content -Path $File -Raw -Encoding UTF8 | & $Mysql @args
    if ($LASTEXITCODE -ne 0) { throw "MySQL failed: $File" }
}

Write-Host "Recreate database ${Database} on ${DbHost}:${Port}"
& $Mysql -h $DbHost -P $Port -u $User "-p$Password" -e "DROP DATABASE IF EXISTS ${Database}; CREATE DATABASE ${Database} DEFAULT CHARSET utf8mb4;"
if ($LASTEXITCODE -ne 0) { throw "Cannot connect to MySQL" }

Invoke-MysqlFile (Join-Path $Root "sql\schema.sql")
Invoke-MysqlFile (Join-Path $Root "sql\ads_schema.sql")
Invoke-MysqlFile (Join-Path $Root "sql\auth_schema.sql")
Invoke-MysqlFile (Join-Path $Root "sql\seed\charging_bigdata_data.sql") -SelectDb
Invoke-MysqlFile (Join-Path $Root "sql\seed\auth_users.sql") -SelectDb

Write-Host ""
Write-Host "[OK] Import done. Start backend + frontend to view charts."
