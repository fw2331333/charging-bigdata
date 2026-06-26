# 打包 Web 演示资源（MySQL 种子 + ML 模型），用于 GitHub Releases 附件
# 用法: powershell -File scripts/package_web_demo.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

& (Join-Path $Root "scripts\export_mysql_seed.ps1")

$Zip = Join-Path $ReleaseDir "web-demo-bundle.zip"
if (Test-Path $Zip) { Remove-Item $Zip }

$Staging = Join-Path $env:TEMP "cbp-web-demo-staging"
if (Test-Path $Staging) { Remove-Item $Staging -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Staging | Out-Null

Copy-Item (Join-Path $Root "sql\schema.sql") $Staging
Copy-Item (Join-Path $Root "sql\ads_schema.sql") $Staging
Copy-Item (Join-Path $Root "sql\seed\charging_bigdata_data.sql") $Staging
$ModelsSrc = Join-Path $Root "analytics\output\models"
if (Test-Path $ModelsSrc) {
    Copy-Item $ModelsSrc (Join-Path $Staging "models") -Recurse
}

Compress-Archive -Path "$Staging\*" -DestinationPath $Zip -Force
Remove-Item $Staging -Recurse -Force

Write-Host "[OK] 已生成: $Zip"
Write-Host "可上传到 GitHub Releases，供他人下载模型 + SQL 种子。"
