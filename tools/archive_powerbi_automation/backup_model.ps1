# Back up the model - fix path escaping
$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdPath) | Out-Null

$port = (Get-Content "C:\Users\bader\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_e00317cc-e952-4283-83d0-8025c8c299fd\Data\msmdsrv.port.txt" -Encoding Unicode).Trim()
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;")
$conn.Open()

$backupPath = "C:/Users/bader/Desktop/CCPRA Project/model_backup.abf"
$backupXmla = '{"backup":{"database":"3b747c39-23bb-417d-96e0-e976777f0047","file":"' + $backupPath + '","allowOverwrite":true}}'

Write-Host "Sending backup command..."
Write-Host $backupXmla
$cmd = $conn.CreateCommand()
$cmd.CommandText = $backupXmla
try {
    $cmd.ExecuteNonQuery() | Out-Null
    Write-Host "Backup successful!"
    $fi = Get-Item "C:\Users\bader\Desktop\CCPRA Project\model_backup.abf"
    Write-Host "Backup file size: $($fi.Length) bytes"
} catch {
    Write-Host "Backup failed: $($_.Exception.Message)"
    
    # Try XMLA format
    Write-Host "`nTrying XMLA format..."
    $xmlaCmd = $conn.CreateCommand()
    $xmlaCmd.CommandText = @"
<Backup xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
  <Object>
    <DatabaseID>3b747c39-23bb-417d-96e0-e976777f0047</DatabaseID>
  </Object>
  <File>C:/Users/bader/Desktop/CCPRA Project/model_backup.abf</File>
  <AllowOverwrite>true</AllowOverwrite>
</Backup>
"@
    try {
        $xmlaCmd.ExecuteNonQuery() | Out-Null
        Write-Host "XMLA Backup successful!"
    } catch {
        Write-Host "XMLA Backup also failed: $($_.Exception.Message)"
    }
}

$conn.Close()
