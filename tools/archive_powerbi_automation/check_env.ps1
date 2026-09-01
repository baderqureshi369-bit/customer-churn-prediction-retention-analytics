$pbi = Get-Process PBIDesktop -ErrorAction SilentlyContinue
if ($pbi) {
    Write-Host "PBIDesktop Processes:"
    $pbi | Select-Object Id, MainWindowTitle, Path | Format-Table -AutoSize
} else {
    Write-Host "No PBIDesktop process found."
}

$msm = Get-Process msmdsrv -ErrorAction SilentlyContinue
if ($msm) {
    Write-Host "msmdsrv Processes:"
    $msm | Select-Object Id, Path | Format-Table -AutoSize
    foreach ($proc in $msm) {
        Write-Host "Listening ports for msmdsrv PID $($proc.Id):"
        Get-NetTCPConnection -OwningProcess $proc.Id -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress, LocalPort, State | Format-Table -AutoSize
    }
} else {
    Write-Host "No msmdsrv process found."
}
