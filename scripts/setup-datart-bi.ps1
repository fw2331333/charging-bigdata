# Seed Datart BI: datasource, MR v1~v7 views (with models), dashboard + share link
param(
    [string]$DatartUrl = "http://127.0.0.1:8088",
    [string]$OrgId = "f8435e0a3323459aaef679ab63fbd01a",
    [string]$MysqlHost = "host.docker.internal",
    [int]$MysqlPort = 3306,
    [string]$MysqlUser = "root",
    [string]$MysqlPassword = "123456",
    [string]$MysqlDatabase = "charging_bigdata",
    [string]$DashboardName = "Charging-BigData-BI",
    [string]$DatartUser = "demo",
    [string]$DatartPassword = "123456"
)

$ErrorActionPreference = "Stop"
$jdbcUrl = "jdbc:mysql://${MysqlHost}:${MysqlPort}/${MysqlDatabase}?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&nullCatalogMeansCurrent=true"

function New-SourceJdbcConfig {
    return @{
        dbType             = 'MYSQL'
        url                = $jdbcUrl
        user               = $MysqlUser
        password           = $MysqlPassword
        driverClass        = 'com.mysql.cj.jdbc.Driver'
        serverAggregate    = $false
        enableSpecialSQL   = $false
        enableSyncSchemas  = $true
        syncInterval       = '60'
        properties         = @{}
    }
}

function Get-DatartHeaders {
    $loginBody = (@{ username = $DatartUser; password = $DatartPassword } | ConvertTo-Json -Compress)
    $r = Invoke-WebRequest -Uri "$DatartUrl/api/v1/users/login" -Method Post -ContentType "application/json" -Body $loginBody -UseBasicParsing
    $script:DatartLoginPayload = $null
    try {
        $script:DatartLoginPayload = $r.Content | ConvertFrom-Json
    } catch {
        $script:DatartLoginPayload = $null
    }
    return @{ Authorization = $r.Headers['Authorization']; 'Content-Type' = 'application/json' }
}

function Resolve-DatartOrgId {
    param([hashtable]$Headers)
    if ($OrgId) { return $OrgId }
    if ($script:DatartLoginPayload -and $script:DatartLoginPayload.data.orgId) {
        return [string]$script:DatartLoginPayload.data.orgId
    }
    $orgs = (Invoke-Datart GET '/api/v1/orgs' $null $Headers).data
    if ($orgs -and $orgs.Count -gt 0) { return [string]$orgs[0].id }
    throw "Cannot resolve Datart orgId; pass -OrgId explicitly."
}

function Invoke-Datart {
    param([string]$Method, [string]$Path, [object]$Body = $null, [hashtable]$Headers)
    if ($Body) {
        return Invoke-RestMethod -Uri "$DatartUrl$Path" -Method $Method -Headers $Headers -Body ($Body | ConvertTo-Json -Depth 12)
    }
    return Invoke-RestMethod -Uri "$DatartUrl$Path" -Method $Method -Headers $Headers
}

function Build-ModelJson {
    param($Columns)
    $cols = @{}
    foreach ($c in $Columns) {
        $key = $c.name[0]
        if ($key -eq 'id') { continue }
        $cols[$key] = @{
            name     = $c.name
            type     = $c.type
            category = 'UNCATEGORIZED'
            path     = @($key)
        }
    }
    # hierarchy must mirror columns; empty hierarchy:{} hides all fields in Datart UI.
    return (@{ version = '1.0'; columns = $cols; hierarchy = $cols } | ConvertTo-Json -Depth 8 -Compress)
}

Write-Host "Datart BI seed -> $DatartUrl"
$h = Get-DatartHeaders
$OrgId = Resolve-DatartOrgId $h
Write-Host "Using orgId=$OrgId user=$DatartUser"

$sources = (Invoke-Datart GET "/api/v1/sources?orgId=$OrgId" $null $h).data
$source = $sources | Where-Object { $_.name -eq 'charging_bigdata' } | Select-Object -First 1
$jdbcConfig = New-SourceJdbcConfig
if ($source) {
    Write-Host "Updating datasource charging_bigdata (JDBC password/host) ..."
    Invoke-Datart PUT "/api/v1/sources/$($source.id)" @{
        id     = $source.id
        name   = 'charging_bigdata'
        type   = 'JDBC'
        orgId  = $OrgId
        config = $jdbcConfig
    } $h | Out-Null
} else {
    Write-Host "Creating datasource charging_bigdata ..."
    $test = @{ name = 'charging_bigdata'; type = 'JDBC'; properties = $jdbcConfig }
    try {
        Invoke-Datart POST '/api/v1/data-provider/test' $test $h | Out-Null
        $source = (Invoke-Datart POST '/api/v1/sources' @{
            name   = 'charging_bigdata'
            type   = 'JDBC'
            orgId  = $OrgId
            config = $jdbcConfig
        } $h).data
    } catch {
        Write-Host "Create source failed: $($_.Exception.Message)"
        Write-Host "Retry login as demo (Datart manual default) or delete old source in UI, then re-run."
        throw
    }
}

$viewDefs = @(
    @{ name = 'v1_voltage_current'; script = 'SELECT record_hour, avg_pack_voltage, avg_charge_current FROM t_voltage_current ORDER BY record_hour' },
    @{ name = 'v2_cell_voltage_range'; script = 'SELECT record_hour, max_cell_voltage, min_cell_voltage FROM t_cell_voltage_range ORDER BY record_hour' },
    @{ name = 'v3_temperature'; script = 'SELECT SUBSTRING(record_time, 1, 10) AS record_hour, MAX(max_temperature) AS max_temperature, MIN(min_temperature) AS min_temperature FROM t_temperature GROUP BY SUBSTRING(record_time, 1, 10) ORDER BY record_hour' },
    @{ name = 'v4_energy_capacity'; script = 'SELECT record_hour, avg_available_energy, avg_available_capacity FROM t_energy_capacity ORDER BY record_hour' },
    @{ name = 'v5_charge_current_stats'; script = 'SELECT record_hour, avg_charge_current, max_charge_current FROM t_charge_current_stats ORDER BY record_hour' },
    @{ name = 'v6_voltage_current_relation'; script = 'SELECT record_hour, voltage_change_rate, current_change_rate FROM t_voltage_current_relation ORDER BY CAST(record_hour AS UNSIGNED)' },
    @{ name = 'v7_soc_temperature'; script = 'SELECT battery_status, avg_max_temperature, avg_min_temperature, var_max_temperature, var_min_temperature FROM t_soc_temperature ORDER BY FIELD(battery_status, ''idle'', ''charging'', ''discharging'')' }
)

$existingViews = (Invoke-Datart GET "/api/v1/views?orgId=$OrgId" $null $h).data
foreach ($def in $viewDefs) {
    $view = $existingViews | Where-Object { $_.name -eq $def.name } | Select-Object -First 1
    if (-not $view) {
        Write-Host "Creating view $($def.name) ..."
        $view = (Invoke-Datart POST '/api/v1/views' @{
            name = $def.name; orgId = $OrgId; sourceId = $source.id; type = 'SQL'; script = $def.script; isFolder = $false
        } $h).data
    }
    $testBody = @{ sourceId = $source.id; script = $def.script; scriptType = 'SQL'; size = 20 }
    $cols = (Invoke-Datart POST '/api/v1/data-provider/execute/test' $testBody $h).data.columns
    $modelJson = Build-ModelJson $cols
    Write-Host "Updating model: $($def.name)"
    Invoke-Datart PUT "/api/v1/views/$($view.id)" @{
        id = $view.id; name = $def.name; orgId = $OrgId; sourceId = $source.id
        type = 'SQL'; script = $def.script; model = $modelJson
    } $h | Out-Null
}

$vizs = (Invoke-Datart GET "/api/v1/viz/folders?orgId=$OrgId" $null $h).data
$dashboardFolder = $vizs | Where-Object { $_.relType -eq 'DASHBOARD' -and $_.name -like '*BI*' } | Select-Object -First 1
if (-not $dashboardFolder) {
    Write-Host "Creating dashboard $DashboardName ..."
    $dashboardFolder = (Invoke-Datart POST '/api/v1/viz/dashboards' @{
        name = $DashboardName; orgId = $OrgId; index = 1; config = '{"type":"auto","version":"1.0.0-RC.3","jsonConfig":{"props":[],"i18ns":[]}}'
    } $h).data
}
$dashboardId = $dashboardFolder.relId

$shares = (Invoke-Datart GET "/api/v1/shares/$dashboardId" $null $h).data
$share = $shares | Select-Object -First 1
if (-not $share) {
    Write-Host "Creating public share ..."
    $share = (Invoke-Datart POST '/api/v1/shares' @{
        vizType = 'DASHBOARD'; vizId = $dashboardId; authenticationMode = 'NONE'
    } $h).data
}

$shareUrl = "$DatartUrl/shareDashboard/$($share.id)?type=NONE"
Write-Host ""
Write-Host "=== Datart BI Ready ==="
Write-Host "Login:    $DatartUrl  ($DatartUser / $DatartPassword)"
Write-Host "Dashboard edit: $DatartUrl/organizations/$OrgId/vizs/$dashboardId"
Write-Host "Share URL: $shareUrl"
Write-Host ""
Write-Host "Next: run scripts/build-datart-dashboard.ps1 to add 7 charts to the dashboard"

# Auto-build dashboard widgets if script exists
$buildScript = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'build-datart-dashboard.ps1'
if (Test-Path $buildScript) {
    Write-Host "Running build-datart-dashboard.ps1 ..."
    & $buildScript -DatartUrl $DatartUrl -OrgId $OrgId -DashboardId $dashboardId -DashboardName $DashboardName -DatartUser $DatartUser -DatartPassword $DatartPassword
}

# Write frontend .env if missing
$envFile = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) '..\frontend\.env'
$envExample = @"
VITE_DATART_BASE_URL=$DatartUrl
VITE_DATART_DASHBOARD_URL=$shareUrl
"@
if (-not (Test-Path $envFile)) {
    Set-Content -Path $envFile -Value $envExample -Encoding utf8
    Write-Host "Wrote frontend/.env"
} else {
    Write-Host "Tip: add to frontend/.env -> VITE_DATART_DASHBOARD_URL=$shareUrl"
}
