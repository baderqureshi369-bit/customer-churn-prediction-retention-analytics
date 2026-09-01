$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdPath) | Out-Null

$port = (Get-Content "C:\Users\bader\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_e00317cc-e952-4283-83d0-8025c8c299fd\Data\msmdsrv.port.txt" -Encoding Unicode).Trim()
$connStr = "Data Source=localhost:$port;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT * FROM `$SYSTEM.DBSCHEMA_CATALOGS"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$ds = New-Object System.Data.DataSet
$adapter.Fill($ds) | Out-Null
Write-Host "CATALOG columns:"
foreach ($col in $ds.Tables[0].Columns) { Write-Host "  $($col.ColumnName): $($ds.Tables[0].Rows[0][$col.ColumnName])" }

$conn.Close()
