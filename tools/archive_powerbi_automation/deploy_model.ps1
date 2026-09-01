# ============================================================================
# CCPRA Power BI Model Deployer
# Deploys the TMSL model to the running Power BI Desktop instance
# ============================================================================

param(
    [string]$TmslPath = "C:\\Users\\bader\\Desktop\\CCPRA Project\powerbi_model.tmsl.json",
    [string]$RefreshPath = "C:\\Users\\bader\\Desktop\\CCPRA Project\powerbi_refresh.tmsl.json"
)

$ErrorActionPreference = "Stop"

# Load AdomdClient
$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
Write-Host "Loading AdomdClient from: $adomdPath"
[System.Reflection.Assembly]::LoadFrom($adomdPath) | Out-Null

# Get port
$portFile = "C:\Users\bader\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_e00317cc-e952-4283-83d0-8025c8c299fd\Data\msmdsrv.port.txt"
$port = (Get-Content $portFile -Encoding Unicode).Trim()
Write-Host "AS Instance port: $port"

# Connect
$connStr = "Data Source=localhost:$port;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()
Write-Host "Connected successfully! State: $($conn.State)"

# Step 1: Deploy model
Write-Host "`n[STEP 1] Deploying data model via TMSL createOrReplace..."
$tmslContent = Get-Content -Path $TmslPath -Raw -Encoding UTF8
$cmd = $conn.CreateCommand()
$cmd.CommandText = $tmslContent
try {
    $cmd.ExecuteNonQuery() | Out-Null
    Write-Host "  -> Model deployed successfully!"
} catch {
    Write-Host "  -> ERROR deploying model: $($_.Exception.Message)"
    Write-Host "  -> Inner: $($_.Exception.InnerException.Message)"
    $conn.Close()
    exit 1
}

# Step 2: Process/Refresh model
Write-Host "`n[STEP 2] Processing model (loading data from CSV)..."
$refreshContent = Get-Content -Path $RefreshPath -Raw -Encoding UTF8
$cmd2 = $conn.CreateCommand()
$cmd2.CommandText = $refreshContent
try {
    $cmd2.ExecuteNonQuery() | Out-Null
    Write-Host "  -> Model processed successfully!"
} catch {
    Write-Host "  -> ERROR processing model: $($_.Exception.Message)"
    Write-Host "  -> Inner: $($_.Exception.InnerException.Message)"
    $conn.Close()
    exit 1
}

# Step 3: Verify tables
Write-Host "`n[STEP 3] Verifying deployed model..."

# Query table count
$cmd3 = $conn.CreateCommand()
$cmd3.CommandText = "SELECT [Name] FROM `$SYSTEM.TMSCHEMA_TABLES"
$adapter3 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd3)
$ds3 = New-Object System.Data.DataSet
$adapter3.Fill($ds3) | Out-Null
Write-Host "  Tables:"
foreach ($row in $ds3.Tables[0].Rows) { Write-Host "    - $($row['Name'])" }

# Verify row counts via DAX
$tables = @(
    @{Name="customer_churn_analytics"; Expected=7043},
    @{Name="risk_category_sort"; Expected=3},
    @{Name="retention_priority_sort"; Expected=4},
    @{Name="Model_Performance"; Expected=2}
)

foreach ($tbl in $tables) {
    $cmd4 = $conn.CreateCommand()
    $cmd4.CommandText = "EVALUATE ROW(""Count"", COUNTROWS('$($tbl.Name)'))"
    $adapter4 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd4)
    $ds4 = New-Object System.Data.DataSet
    $adapter4.Fill($ds4) | Out-Null
    $count = $ds4.Tables[0].Rows[0][0]
    $status = if ($count -eq $tbl.Expected) { "OK" } else { "MISMATCH (expected $($tbl.Expected))" }
    Write-Host "    $($tbl.Name): $count rows - $status"
}

# Verify key measures
Write-Host "`n  Verifying measures..."
$measureChecks = @(
    @{DAX='EVALUATE ROW("v", [Total Customers])'; Expected=7043; Name="Total Customers"},
    @{DAX='EVALUATE ROW("v", [Actual Churned Customers])'; Expected=1869; Name="Actual Churned Customers"},
    @{DAX='EVALUATE ROW("v", [Actual Retained Customers])'; Expected=5174; Name="Actual Retained Customers"},
    @{DAX='EVALUATE ROW("v", [Predicted Churn Customers])'; Expected=1562; Name="Predicted Churn Customers"},
    @{DAX='EVALUATE ROW("v", [High Risk Customers])'; Expected=1039; Name="High Risk Customers"},
    @{DAX='EVALUATE ROW("v", [Critical Priority Customers])'; Expected=49; Name="Critical Priority Customers"},
    @{DAX='EVALUATE ROW("v", [High Priority Customers])'; Expected=990; Name="High Priority Customers"},
    @{DAX='EVALUATE ROW("v", [Medium Priority Customers])'; Expected=1633; Name="Medium Priority Customers"},
    @{DAX='EVALUATE ROW("v", [Low Priority Customers])'; Expected=4371; Name="Low Priority Customers"}
)

foreach ($chk in $measureChecks) {
    $cmd5 = $conn.CreateCommand()
    $cmd5.CommandText = $chk.DAX
    $adapter5 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd5)
    $ds5 = New-Object System.Data.DataSet
    $adapter5.Fill($ds5) | Out-Null
    $val = $ds5.Tables[0].Rows[0][0]
    $status = if ([int]$val -eq $chk.Expected) { "OK" } else { "MISMATCH (expected $($chk.Expected), got $val)" }
    Write-Host "    $($chk.Name): $val - $status"
}

# Verify relationships
Write-Host "`n  Verifying relationships..."
$cmd6 = $conn.CreateCommand()
$cmd6.CommandText = "SELECT [Name], [FromTableID], [ToTableID] FROM `$SYSTEM.TMSCHEMA_RELATIONSHIPS"
$adapter6 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd6)
$ds6 = New-Object System.Data.DataSet
$adapter6.Fill($ds6) | Out-Null
foreach ($row in $ds6.Tables[0].Rows) { Write-Host "    - $($row['Name'])" }

# Count measures
$cmd7 = $conn.CreateCommand()
$cmd7.CommandText = "SELECT [Name] FROM `$SYSTEM.TMSCHEMA_MEASURES"
$adapter7 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd7)
$ds7 = New-Object System.Data.DataSet
$adapter7.Fill($ds7) | Out-Null
Write-Host "`n  Total measures: $($ds7.Tables[0].Rows.Count)"
foreach ($row in $ds7.Tables[0].Rows) { Write-Host "    - $($row['Name'])" }

$conn.Close()
Write-Host "`n============================================"
Write-Host "MODEL DEPLOYMENT COMPLETE"
Write-Host "============================================"
