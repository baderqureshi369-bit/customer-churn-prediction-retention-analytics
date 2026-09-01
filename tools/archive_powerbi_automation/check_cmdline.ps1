$proc = Get-CimInstance Win32_Process -Filter "ProcessId = 15140"
Write-Host "msmdsrv CommandLine:"
Write-Host $proc.CommandLine

$pbiProc = Get-CimInstance Win32_Process -Filter "ProcessId = 17016"
Write-Host "PBIDesktop CommandLine:"
Write-Host $pbiProc.CommandLine
