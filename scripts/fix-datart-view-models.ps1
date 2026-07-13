# Fix view models: remove empty hierarchy so Datart field list loads.
param(
    [string]$DatartUrl = "http://127.0.0.1:8088",
    [string]$OrgId = "f8435e0a3323459aaef679ab63fbd01a"
)

$ErrorActionPreference = "Stop"
$h = (Invoke-WebRequest -Uri "$DatartUrl/api/v1/users/login" -Method Post -ContentType "application/json" -Body '{"username":"demo","password":"123456"}' -UseBasicParsing).Headers['Authorization']
$headers = @{ Authorization = $h; 'Content-Type' = 'application/json' }

$views = (Invoke-RestMethod -Uri "$DatartUrl/api/v1/views?orgId=$OrgId" -Headers $headers).data
foreach ($view in $views) {
    if ($view.isFolder) { continue }
    $full = (Invoke-RestMethod -Uri "$DatartUrl/api/v1/views/$($view.id)" -Headers $headers).data
    if (-not $full.model) {
        Write-Host "Skip (no model): $($view.name)"
        continue
    }
    $model = $full.model | ConvertFrom-Json
    if (-not $model.columns) { continue }
    $cols = @{}
    $model.columns.PSObject.Properties | ForEach-Object {
        $v = @{}
        $_.Value.PSObject.Properties | ForEach-Object { $v[$_.Name] = $_.Value }
        if (-not $v.path) { $v.path = @($_.Name) }
        $cols[$_.Name] = $v
    }
    $fixed = @{ version = $model.version; columns = $cols; hierarchy = $cols }
    $modelJson = ($fixed | ConvertTo-Json -Depth 8 -Compress)
    Write-Host "Fix model: $($view.name)"
    Invoke-RestMethod -Uri "$DatartUrl/api/v1/views/$($view.id)" -Method PUT -Headers $headers -Body (@{
        id = $view.id; name = $view.name; orgId = $OrgId; sourceId = $full.sourceId
        type = $full.type; script = $full.script; model = $modelJson
    } | ConvertTo-Json -Depth 8) | Out-Null
}

Write-Host "Done. Rebuilding dashboard ..."
& (Join-Path $PSScriptRoot 'build-datart-dashboard.ps1') -DatartUrl $DatartUrl -OrgId $OrgId
