# Create 7 Datart charts (v1-v7) and place them on the BI dashboard grid.
# Datart image: 1.0.0-rc.3 — widget/chart config must match its migration schema.
param(
    [string]$DatartUrl = "http://127.0.0.1:8088",
    [string]$OrgId = "f8435e0a3323459aaef679ab63fbd01a",
    [string]$DashboardId = "5f6304328157487ab51c1bbba5723cee",
    [string]$DashboardName = "Charging-BigData-BI",
    [string]$DatartUser = "admin",
    [string]$DatartPassword = "123456"
)

$ErrorActionPreference = "Stop"
$DatartVersion = '1.0.0-RC.3'
$WidgetVersion = '1.0.0-RC.3'
$DecimalPlaces = 1
# RC.3 share page: keep widget chrome minimal; chart styles stay empty via builders below.
$WidgetCustomConfig = Get-Content (Join-Path $PSScriptRoot 'datart-linked-widget-custom.json') -Raw -Encoding UTF8 | ConvertFrom-Json

function Get-DatartHeaders {
    $loginBody = (@{ username = $DatartUser; password = $DatartPassword } | ConvertTo-Json -Compress)
    $r = Invoke-WebRequest -Uri "$DatartUrl/api/v1/users/login" -Method Post -ContentType "application/json" -Body $loginBody -UseBasicParsing
    return @{ Authorization = $r.Headers['Authorization']; 'Content-Type' = 'application/json' }
}

function Invoke-Datart {
    param([string]$Method, [string]$Path, [object]$Body = $null, [hashtable]$Headers)
    if ($Body) {
        return Invoke-RestMethod -Uri "$DatartUrl$Path" -Method $Method -Headers $Headers -Body ($Body | ConvertTo-Json -Depth 24 -Compress)
    }
    return Invoke-RestMethod -Uri "$DatartUrl$Path" -Method $Method -Headers $Headers
}

# PowerShell ConvertTo-Json collapses single-element arrays to objects — breaks Datart metrics.rows.
function ConvertTo-DatartConfigJson {
    param([object]$Config)
    $json = $Config | ConvertTo-Json -Depth 20 -Compress
    $json = [regex]::Replace(
        $json,
        '"key":"metrics","rows":(\{(?:[^{}]|(?<open>\{)|(?<-open>\}))+(?(open)(?!))\})',
        '"key":"metrics","rows":[$1]'
    )
    $json = [regex]::Replace(
        $json,
        '"key":"dimension","rows":(\{(?:[^{}]|(?<open>\{)|(?<-open>\}))+(?(open)(?!))\})',
        '"key":"dimension","rows":[$1]'
    )
    return $json
}

function New-NumericFormat {
    return @{
        type    = 'numeric'
        numeric = @{
            decimalPlaces        = $DecimalPlaces
            unitKey              = 'none'
            useThousandSeparator = $false
            prefix               = ''
            suffix               = ''
        }
    }
}

function New-PercentageFormat {
    param([int]$Places = 2)
    return @{
        type       = 'percentage'
        percentage = @{ decimalPlaces = $Places }
    }
}

function Get-ChartMarginStyles {
    # Balanced margins: enough room for axes/legend without shrinking the plot area.
    return @{
        label = 'margin'; key = 'margin'; comType = 'group'
        rows  = @(
            @{ label = 'viz.palette.style.margin.containLabel'; key = 'containLabel'; value = $true; comType = 'checkbox' }
            @{ label = 'viz.palette.style.margin.left'; key = 'marginLeft'; value = '12%'; comType = 'marginWidth' }
            @{ label = 'viz.palette.style.margin.right'; key = 'marginRight'; value = '4%'; comType = 'marginWidth' }
            @{ label = 'viz.palette.style.margin.top'; key = 'marginTop'; value = '11%'; comType = 'marginWidth' }
            @{ label = 'viz.palette.style.margin.bottom'; key = 'marginBottom'; value = '18%'; comType = 'marginWidth' }
        )
    }
}

function Get-XAxisSpacingStyles {
    return @{
        label = 'xAxis.title'; key = 'xAxis'; comType = 'group'
        rows  = @(
            @{ label = 'common.rotate'; key = 'rotate'; value = 45; comType = 'inputNumber' }
            @{ label = 'common.showInterval'; key = 'showInterval'; value = $true; comType = 'checkbox' }
            @{ label = 'common.interval'; key = 'interval'; value = 0; comType = 'inputNumber' }
        )
    }
}

function Get-YAxisModalRow {
    # Datart reads yAxis.modal.YAxisNumberFormat as an array for axis tick formatting.
    # Use value=[] only — do NOT include YAxisNumberFormatPanel (breaks share page rendering).
    return @{
        label = 'yAxis.open'; key = 'modal'; comType = 'group'
        options = @{
            type       = 'modal'
            modalSize  = 'middle'
            flatten    = $true
            title      = 'yAxis.numberFormat'
        }
        rows  = @(
            @{ label = 'yAxis.open'; key = 'YAxisNumberFormat'; value = @() }
        )
    }
}

function Get-SplitLineStyles {
    return @{
        label = 'splitLine.title'; key = 'splitLine'; comType = 'group'
        rows  = @(
            @{ label = 'splitLine.showHorizonLine'; key = 'showHorizonLine'; value = $true; comType = 'checkbox' }
            @{
                label = 'common.lineStyle'; key = 'horizonLineStyle'; comType = 'line'
                value = @{ type = 'dashed'; width = 1; color = '#ced4da' }
            }
        )
    }
}

function Get-YAxisSpacingStyles {
    # Short metric aliases + moderate nameGap avoid title/tick overlap without huge left margin.
    return @{
        label = 'yAxis.title'; key = 'yAxis'; comType = 'group'
        rows  = @(
            @{ label = 'common.showAxis'; key = 'showAxis'; value = $true; comType = 'checkbox' }
            @{ label = 'common.showLabel'; key = 'showLabel'; value = $true; comType = 'checkbox' }
            @{ label = 'common.showTitleAndUnit'; key = 'showTitleAndUnit'; value = $true; comType = 'checkbox' }
            @{
                label = 'viz.palette.style.font'; key = 'font'; comType = 'font'
                value = @{
                    fontFamily = 'PingFang SC'; fontSize = '10'
                    fontWeight = 'normal'; fontStyle = 'normal'; color = '#495057'
                }
            }
            @{ label = 'common.nameLocation'; key = 'nameLocation'; value = 'center'; comType = 'nameLocation' }
            @{ label = 'common.nameRotate'; key = 'nameRotate'; value = 90; comType = 'inputNumber' }
            @{ label = 'common.nameGap'; key = 'nameGap'; value = 46; comType = 'inputNumber' }
            (Get-YAxisModalRow)
        )
    }
}

function Get-BarSpacingStyles {
    return @{
        label = 'bar.title'; key = 'bar'; comType = 'group'
        rows  = @(
            @{ label = 'bar.gap'; key = 'gap'; value = 0.38; comType = 'inputPercentage' }
            @{ label = 'bar.width'; key = 'width'; value = 0; comType = 'inputNumber' }
        )
    }
}

function Get-LabelSpacingStyles {
    param([bool]$ShowLabel = $true, [string]$FontSize = '9')
    return @{
        label = 'label.title'; key = 'label'; comType = 'group'
        rows  = @(
            @{ label = 'label.showLabel'; key = 'showLabel'; value = $ShowLabel; comType = 'checkbox' }
            @{ label = 'label.position'; key = 'position'; value = 'top'; comType = 'labelPosition' }
            @{
                label = 'viz.palette.style.font'; key = 'font'; comType = 'font'
                value = @{
                    fontFamily = 'PingFang SC'; fontSize = $FontSize
                    fontWeight = 'normal'; fontStyle = 'normal'; color = '#495057'
                }
            }
        )
    }
}

function Get-CartesianSpacingStyles {
    param([bool]$ShowDataLabel = $true, [switch]$WithBarGap)
    # margin + xAxis only; custom yAxis rows cause RC.3 share-page "t.forEach" errors
    $styles = @(
        (Get-ChartMarginStyles),
        (Get-XAxisSpacingStyles),
        (Get-SplitLineStyles),
        (Get-LabelSpacingStyles -ShowLabel $ShowDataLabel -FontSize '9')
    )
    if ($WithBarGap) { $styles += Get-BarSpacingStyles }
    return $styles
}

function Get-PieSpacingStyles {
    return @(
        (Get-ChartMarginStyles),
        (Get-LabelSpacingStyles -ShowLabel $true -FontSize '10'),
        @{
            label = 'legend.title'; key = 'legend'; comType = 'group'
            rows  = @(
                @{ label = 'legend.showLegend'; key = 'showLegend'; value = $true; comType = 'checkbox' }
                @{ label = 'legend.position'; key = 'position'; value = 'right'; comType = 'legendPosition' }
            )
        }
    )
}

function New-Field {
    param([string]$ColName, [string]$Type, [string]$Aggregate = '')
    return @{
        colName   = $ColName
        type      = $Type
        category  = 'field'
        uid       = [guid]::NewGuid().ToString('N')
        aggregate = $Aggregate
    }
}

function New-MetricField {
    param(
        [string]$ColName,
        [ValidateSet('numeric', 'percentage')]
        [string]$FormatType = 'numeric',
        [string]$Alias = ''
    )
    $field = New-Field $ColName 'NUMERIC' ''
    if ($Alias) { $field.alias = @{ name = $Alias } }
    $field.format = if ($FormatType -eq 'percentage') { New-PercentageFormat 2 } else { New-NumericFormat }
    return $field
}

function New-MetricRows {
    param(
        [string[]]$Metrics,
        [hashtable]$Aliases = @{},
        [ValidateSet('numeric', 'percentage')]
        [string]$FormatType = 'numeric',
        [switch]$Plain
    )
    if ($Plain) {
        return @($Metrics | ForEach-Object { New-Field $_ 'NUMERIC' })
    }
    return @($Metrics | ForEach-Object {
            $alias = if ($Aliases.ContainsKey($_)) { $Aliases[$_] } else { '' }
            New-MetricField $_ $FormatType $alias
        })
}

function New-DataChartConfig {
    param(
        [string]$ChartGraphId,
        [array]$Datas,
        [array]$Styles = @()
    )
    return @{
        aggregation    = $false
        chartGraphId   = $ChartGraphId
        computedFields = @()
        chartConfig    = @{
            datas        = $Datas
            styles       = $Styles
            settings     = @()
            interactions = @()
            i18ns        = @()
        }
    }
}

function New-LineChartConfig {
    param([string]$Dim, [string[]]$Metrics, [hashtable]$Aliases = @{})
    return New-DataChartConfig 'line-chart' @(
        @{ label = 'dimension'; key = 'dimension'; type = 'group'; rows = @((New-Field $Dim 'STRING')) },
        @{ label = 'metrics'; key = 'metrics'; type = 'aggregate'; rows = @(New-MetricRows $Metrics $Aliases) }
    ) (Get-DoubleYSpacingStyles)
}

function New-DoubleYChartConfig {
    param(
        [string]$Dim,
        [string[]]$Left,
        [string[]]$Right,
        [hashtable]$Aliases = @{}
    )
    return New-DataChartConfig 'double-y' @(
        @{ label = 'dimension'; key = 'dimension'; type = 'group'; rows = @((New-Field $Dim 'STRING')) },
        @{ label = 'axis.y.left'; key = 'metricsL'; type = 'aggregate'; rows = @(New-MetricRows $Left $Aliases) },
        @{ label = 'axis.y.right'; key = 'metricsR'; type = 'aggregate'; rows = @(New-MetricRows $Right $Aliases) }
    ) (Get-DoubleYSpacingStyles)
}

function Get-DoubleYSpacingStyles {
    return @(
        (Get-ChartMarginStyles),
        (Get-XAxisSpacingStyles),
        (Get-SplitLineStyles),
        (Get-LabelSpacingStyles -ShowLabel $false -FontSize '9')
    )
}

function New-ScatterChartConfig {
    param([string]$X, [string]$Y)
    return New-DataChartConfig 'scatter' @(
        @{ label = 'metrics'; key = 'metrics'; type = 'aggregate'; rows = @((New-MetricField $X), (New-MetricField $Y)) }
    )
}

function New-ColumnChartConfig {
    param([string]$Dim, [string[]]$Metrics, [hashtable]$Aliases = @{})
    return New-DataChartConfig 'cluster-column-chart' @(
        @{ label = 'dimension'; key = 'dimension'; type = 'group'; rows = @((New-Field $Dim 'STRING')) },
        @{ label = 'metrics'; key = 'metrics'; type = 'aggregate'; rows = @(New-MetricRows $Metrics $Aliases) }
    ) (Get-CartesianSpacingStyles -ShowDataLabel:$false -WithBarGap)
}

function New-PieChartConfig {
    param([string]$Dim, [string[]]$Metrics)
    return New-DataChartConfig 'pie-chart' @(
        @{ label = 'dimension'; key = 'dimension'; type = 'group'; rows = @((New-Field $Dim 'STRING')) },
        @{ label = 'metrics'; key = 'metrics'; type = 'aggregate'; rows = @($Metrics | ForEach-Object { New-MetricField $_ 'percentage' }) }
    ) (Get-PieSpacingStyles)
}

function New-DoughnutChartConfig {
    param([string]$Dim, [string[]]$Metrics)
    return New-DataChartConfig 'doughnut-chart' @(
        @{ label = 'dimension'; key = 'dimension'; type = 'group'; rows = @((New-Field $Dim 'STRING')) },
        @{ label = 'metrics'; key = 'metrics'; type = 'aggregate'; rows = @($Metrics | ForEach-Object { New-MetricField $_ 'numeric' }) }
    ) (Get-PieSpacingStyles)
}

function New-AreaChartConfig {
    param([string]$Dim, [string[]]$Metrics, [hashtable]$Aliases = @{})
    return New-DataChartConfig 'area-chart' @(
        @{ label = 'dimension'; key = 'dimension'; type = 'group'; rows = @((New-Field $Dim 'STRING')) },
        @{ label = 'metrics'; key = 'metrics'; type = 'aggregate'; rows = @(New-MetricRows $Metrics $Aliases) }
    ) (Get-CartesianSpacingStyles -ShowDataLabel:$false)
}

function New-StackAreaChartConfig {
    param([string]$Dim, [string[]]$Metrics, [hashtable]$Aliases = @{})
    return New-DataChartConfig 'stack-area-chart' @(
        @{ label = 'dimension'; key = 'dimension'; type = 'group'; rows = @((New-Field $Dim 'STRING')) },
        @{ label = 'metrics'; key = 'metrics'; type = 'aggregate'; rows = @(New-MetricRows $Metrics $Aliases) }
    ) (Get-CartesianSpacingStyles -ShowDataLabel:$false)
}

function New-Widget {
    param(
        [string]$DashId, [string]$ChartId, [string]$ViewId, [string]$Name,
        [int]$X, [int]$Y, [int]$W, [int]$H,
        [int]$Index = 0
    )
    $wid = [guid]::NewGuid().ToString('N')
    $clientId = 'client_' + [guid]::NewGuid().ToString('N')
    # RC.3 linkedChart widget shape (matches dataChartCreator output)
    $widgetConfig = @{
        version      = $WidgetVersion
        clientId     = $clientId
        index        = $Index
        name         = $Name
        boardType    = 'auto'
        type         = 'chart'
        originalType = 'linkedChart'
        lock         = $false
        content      = @{}
        rect         = @{ x = 0; y = 0; width = 400; height = 300 }
        pRect        = @{ x = $X; y = $Y; width = $W; height = $H }
        customConfig = $WidgetCustomConfig
    }
    return @{
        id          = "linkedChart$wid"
        dashboardId = $DashId
        datachartId = $ChartId
        parentId    = ''
        viewIds     = @($ViewId)
        relations   = @()
        config      = ($widgetConfig | ConvertTo-Json -Depth 16 -Compress)
    }
}

# Taller grid rows (h=6) — more plot area per widget; y steps of 6
# Layout matches local MrBiView / visu1.png: 2-col grid, v7 full width bottom row
$chartDefs = @(
  @{ name='chart_v1'; view='v1_voltage_current'; title='v1_voltage_current'; cfg=(New-ColumnChartConfig 'record_hour' @('avg_pack_voltage','avg_charge_current') @{ avg_pack_voltage='voltage'; avg_charge_current='current' }); layout=@{x=0;y=0;w=6;h=6} },
  @{ name='chart_v2'; view='v2_cell_voltage_range'; title='v2_cell_voltage_range'; cfg=(New-ColumnChartConfig 'record_hour' @('max_cell_voltage','min_cell_voltage') @{ max_cell_voltage='max_V'; min_cell_voltage='min_V' }); layout=@{x=6;y=0;w=6;h=6} },
  @{ name='chart_v3'; view='v3_temperature'; title='v3_temperature'; cfg=(New-LineChartConfig 'record_hour' @('max_temperature','min_temperature') @{ max_temperature='max_T'; min_temperature='min_T' }); layout=@{x=0;y=6;w=6;h=6} },
  @{ name='chart_v4'; view='v4_energy_capacity'; title='v4_energy_capacity'; cfg=(New-StackAreaChartConfig 'record_hour' @('avg_available_energy','avg_available_capacity') @{ avg_available_energy='energy'; avg_available_capacity='capacity' }); layout=@{x=6;y=6;w=6;h=6} },
  @{ name='chart_v5'; view='v5_charge_current_stats'; title='v5_charge_current_stats'; cfg=(New-ColumnChartConfig 'record_hour' @('max_charge_current','avg_charge_current') @{ max_charge_current='max_I'; avg_charge_current='avg_I' }); layout=@{x=0;y=12;w=6;h=6} },
  @{ name='chart_v6'; view='v6_voltage_current_relation'; title='v6_voltage_change_rate'; cfg=(New-LineChartConfig 'record_hour' @('voltage_change_rate','current_change_rate') @{ voltage_change_rate='V_chg_%'; current_change_rate='I_chg_%' }); layout=@{x=6;y=12;w=6;h=6} },
  @{ name='chart_v7'; view='v7_soc_temperature'; title='v7_battery_status_temperature'; cfg=(New-DoubleYChartConfig 'battery_status' @('avg_max_temperature','avg_min_temperature') @('var_max_temperature','var_min_temperature') @{ avg_max_temperature='avg_max_T'; avg_min_temperature='avg_min_T'; var_max_temperature='var_max_T'; var_min_temperature='var_min_T' }); layout=@{x=0;y=18;w=12;h=6} }
)

Write-Host "Building Datart dashboard at $DatartUrl (Datart $DatartVersion) ..."
$h = Get-DatartHeaders

$views = (Invoke-Datart GET "/api/v1/views?orgId=$OrgId" $null $h).data
$folders = (Invoke-Datart GET "/api/v1/viz/folders?orgId=$OrgId" $null $h).data
$existingCharts = $folders | Where-Object { $_.relType -eq 'DATACHART' }

foreach ($def in $chartDefs) {
    $view = $views | Where-Object { $_.name -eq $def.view } | Select-Object -First 1
    if (-not $view) { throw "View not found: $($def.view)" }

    $folder = $existingCharts | Where-Object { $_.name -eq $def.name } | Select-Object -First 1
    $configObj = ConvertTo-DatartConfigJson $def.cfg | ConvertFrom-Json

    if ($folder) {
        Write-Host "Updating chart $($def.name) ..."
        Invoke-Datart PUT "/api/v1/viz/datacharts/$($folder.relId)" @{
            id = $folder.relId; name = $def.name; orgId = $OrgId; viewId = $view.id; config = $configObj
        } $h | Out-Null
    } else {
        Write-Host "Creating chart $($def.name) ..."
        Invoke-Datart POST '/api/v1/viz/datacharts' @{
            name = $def.name; orgId = $OrgId; viewId = $view.id; config = $configObj
        } $h | Out-Null
    }
}

$folders = (Invoke-Datart GET "/api/v1/viz/folders?orgId=$OrgId" $null $h).data
$chartFolders = $folders | Where-Object { $_.relType -eq 'DATACHART' }
$chartIds = @{}
foreach ($def in $chartDefs) {
    $folder = $chartFolders | Where-Object { $_.name -eq $def.name } | Select-Object -First 1
    if (-not $folder) { throw "Chart folder not found: $($def.name)" }
    $chartIds[$def.name] = $folder.relId
}

# initAutoBoardConfig() — ASCII only (Chinese i18n breaks JSON via API encoding)
$autoBoardConfig = '{"type":"auto","version":"1.0.0-RC.3","jsonConfig":{"props":[{"label":"basic.basic","key":"basic","comType":"group","rows":[{"label":"basic.initialQuery","key":"initialQuery","value":true,"comType":"switch"},{"label":"basic.allowOverlap","key":"allowOverlap","value":false,"comType":"switch"}]},{"label":"space.space","key":"space","comType":"group","rows":[{"label":"space.paddingTB","key":"paddingTB","default":14,"value":14,"comType":"inputNumber"},{"label":"space.paddingLR","key":"paddingLR","default":14,"value":14,"comType":"inputNumber"},{"label":"space.marginTB","key":"marginTB","default":16,"value":16,"comType":"inputNumber"},{"label":"space.marginLR","key":"marginLR","default":14,"value":14,"comType":"inputNumber"}]},{"label":"mSpace.mSpace","key":"mSpace","comType":"group","rows":[{"label":"mSpace.paddingTB","key":"paddingTB","default":14,"value":14,"comType":"inputNumber"},{"label":"mSpace.paddingLR","key":"paddingLR","default":14,"value":14,"comType":"inputNumber"},{"label":"mSpace.marginTB","key":"marginTB","default":16,"value":16,"comType":"inputNumber"},{"label":"mSpace.marginLR","key":"marginLR","default":14,"value":14,"comType":"inputNumber"}]},{"label":"background.background","key":"background","comType":"group","rows":[{"label":"background.background","key":"background","default":{"color":"transparent","image":"","size":"100% 100%","repeat":"no-repeat"},"value":{"color":"transparent","image":"","size":"100% 100%","repeat":"no-repeat"},"comType":"background"}]}],"i18ns":[]}}'

$dash = (Invoke-Datart GET "/api/v1/viz/dashboards/$DashboardId" $null $h).data
$deleteIds = @($dash.widgets | ForEach-Object { $_.id })

$widgets = @()
$widgetIndex = 0
foreach ($def in $chartDefs) {
    $view = $views | Where-Object { $_.name -eq $def.view } | Select-Object -First 1
    $widgets += New-Widget $DashboardId $chartIds[$def.name] $view.id $def.title $def.layout.x $def.layout.y $def.layout.w $def.layout.h $widgetIndex
    $widgetIndex++
}

Write-Host "Placing $($widgets.Count) widgets on dashboard ..."
Invoke-Datart PUT "/api/v1/viz/dashboards/$DashboardId" @{
    id              = $DashboardId
    name            = $DashboardName
    orgId           = $OrgId
    index           = 1
    config          = $autoBoardConfig
    widgetToCreate  = $widgets
    widgetToUpdate  = @()
    widgetToDelete  = $deleteIds
} $h | Out-Null

# Fix garbled folder display name (ASCII only)
$dashFolder = $folders | Where-Object { $_.relType -eq 'DASHBOARD' -and $_.relId -eq $DashboardId } | Select-Object -First 1
if ($dashFolder -and $dashFolder.name -ne $DashboardName) {
    Write-Host "Renaming dashboard folder to $DashboardName ..."
    Invoke-Datart PUT "/api/v1/viz/folders/$($dashFolder.id)" @{
        id = $dashFolder.id; name = $DashboardName; orgId = $OrgId; index = $dashFolder.index
        relType = 'DASHBOARD'; relId = $DashboardId; parentId = $dashFolder.parentId
    } $h | Out-Null
}

Invoke-Datart PUT "/api/v1/viz/publish/$DashboardId`?vizType=DASHBOARD" $null $h | Out-Null
foreach ($chartId in $chartIds.Values) {
    Invoke-Datart PUT "/api/v1/viz/publish/$chartId`?vizType=DATACHART" $null $h | Out-Null
}

$shares = (Invoke-Datart GET "/api/v1/shares/$DashboardId" $null $h).data
$share = $shares | Select-Object -First 1
$shareUrl = if ($share) { "$DatartUrl/shareDashboard/$($share.id)?type=NONE" } else { "$DatartUrl/organizations/$OrgId/vizs/$DashboardId" }

Write-Host ""
Write-Host "=== Dashboard Ready ==="
Write-Host "Widgets: $($widgets.Count)"
Write-Host "Share:   $shareUrl"
Write-Host "Read:    $DatartUrl/organizations/$OrgId/vizs/$DashboardId"
Write-Host "Edit:    $DatartUrl/organizations/$OrgId/vizs/$DashboardId/boardEditor"
