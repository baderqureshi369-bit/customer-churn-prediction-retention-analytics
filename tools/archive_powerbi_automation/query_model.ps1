$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdPath) | Out-Null

$portFile = "C:\Users\bader\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_e00317cc-e952-4283-83d0-8025c8c299fd\Data\msmdsrv.port.txt"
$port = (Get-Content $portFile -Encoding Unicode).Trim()

$connStr = "Data Source=localhost:$port;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [ID], [Name] FROM `$SYSTEM.TMSCHEMA_TABLES"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$ds = New-Object System.Data.DataSet
$adapter.Fill($ds) | Out-Null
Write-Host "TMSCHEMA_TABLES:"
$ds.Tables[0] | Format-Table -AutoSize

$cmd2 = $conn.CreateCommand()
$cmd2.CommandText = "SELECT [ID], [TableID], [Name], [DataType] FROM `$SYSTEM.TMSCHEMA_COLUMNS"
$adapter2 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd2)
$ds2 = New-Object System.Data.DataSet
$adapter2.Fill($ds2) | Out-Null
Write-Host "TMSCHEMA_COLUMNS count: $($ds2.Tables[0].Rows.Count)"

$conn.Close()
