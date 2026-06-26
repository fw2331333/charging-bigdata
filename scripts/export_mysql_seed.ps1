# 维护者：从本机 MySQL 导出 Web 演示种子数据
# 用法: powershell -File scripts/export_mysql_seed.ps1
param(
    [string]$Mysqldump = "mysqldump",
    [string]$Host = "127.0.0.1",
    [string]$User = "root",
    [string]$Password = "123456",
    [string]$Database = "charging_bigdata"
)

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Out = Join-Path $Root "sql\seed\charging_bigdata_data.sql"
New-Item -ItemType Directory -Force -Path (Split-Path $Out) | Out-Null

$Tables = @(
    "t_voltage_current", "t_cell_voltage_range", "t_temperature",
    "t_energy_capacity", "t_charge_current_stats", "t_voltage_current_relation",
    "t_soc_temperature", "t_soc_hourly", "t_charging_daily", "t_charging_monthly",
    "t_charge_rate_hourly", "t_soc_heatmap"
)

& $Mysqldump -h $Host -u $User "-p$Password" --no-create-info --skip-triggers --complete-insert `
    $Database $Tables | Out-File -FilePath $Out -Encoding utf8

Write-Host "[OK] 已导出: $Out ($((Get-Item $Out).Length) bytes)"
