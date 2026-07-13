# Start Datart BI (manual section 5.2)
# Maps host 8088 -> container 8080 to avoid conflict with Vue on 8080

param(
    [int]$Port = 8088,
    [string]$Name = "cbp-datart",
    [switch]$UseMysqlConf
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$confName = if ($UseMysqlConf) { "datart-mysql.conf" } else { "datart.conf" }
$confPath = Join-Path $root "docker\datart\$confName"

if (-not (Test-Path $confPath)) {
    throw "Config not found: $confPath"
}

$existing = docker ps -a --filter "name=^${Name}$" --format "{{.Names}}"
if ($existing -eq $Name) {
    $running = docker ps --filter "name=^${Name}$" --format "{{.Names}}"
    if ($running -eq $Name) {
        Write-Host "Datart already running at http://127.0.0.1:$Port (login demo/123456)"
        exit 0
    }
    Write-Host "Starting existing container $Name ..."
    docker start $Name | Out-Null
} else {

    Write-Host "Starting Datart at http://127.0.0.1:$Port (login demo/123456)"
    docker run -d `
        --name $Name `
        -p "${Port}:8080" `
        -v "${confPath}:/datart/config/datart.conf" `
        -v cbp_datart_files:/datart/files `
        datart/datart | Out-Null
}

Write-Host "Done. See docs/Datart-BI大屏部署手册.md for charging_bigdata datasource setup."
