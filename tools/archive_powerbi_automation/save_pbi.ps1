# Use COM automation to send Ctrl+Shift+S (Save As) to Power BI Desktop
# and programmatically fill in the save dialog

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

# Find PBI Desktop process
$pbi = Get-Process -Name PBIDesktop -ErrorAction SilentlyContinue
if (-not $pbi) {
    Write-Host "Power BI Desktop is not running!"
    exit 1
}

Write-Host "Found PBI Desktop PID: $($pbi.Id)"

# Use SetForegroundWindow to bring PBI to focus
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class WindowHelper {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    
    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr FindWindowEx(IntPtr hwndParent, IntPtr hwndChildAfter, string lpszClass, string lpszWindow);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    
    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@

# Find the actual PBI main window
$targetPid = $pbi.Id
$foundHwnd = [IntPtr]::Zero

[WindowHelper]::EnumWindows({
    param($hwnd, $lparam)
    $pid = 0
    [WindowHelper]::GetWindowThreadProcessId($hwnd, [ref]$pid) | Out-Null
    if ($pid -eq $targetPid -and [WindowHelper]::IsWindowVisible($hwnd)) {
        $sb = New-Object System.Text.StringBuilder 512
        [WindowHelper]::GetWindowText($hwnd, $sb, $sb.Capacity) | Out-Null
        $title = $sb.ToString()
        if ($title.Length -gt 0) {
            Write-Host "Found window: HWND=$hwnd Title='$title'"
            $script:foundHwnd = $hwnd
        }
    }
    return $true
}, [IntPtr]::Zero) | Out-Null

if ($foundHwnd -eq [IntPtr]::Zero) {
    Write-Host "Could not find PBI Desktop window. Trying alternate approach..."
    # The PBI might have its main window handle at 0 from our session
    # Let's try to use the process directly
    $foundHwnd = $pbi.MainWindowHandle
    if ($foundHwnd -eq [IntPtr]::Zero) {
        Write-Host "PBI Desktop window handle is 0 - this process likely runs in a different desktop session."
        Write-Host "Cannot automate Save via SendKeys from this session."
        Write-Host ""
        Write-Host "ALTERNATIVE: The user must manually save the file:"
        Write-Host "1. Open Power BI Desktop (it should already show the loaded model)"
        Write-Host "2. Press Ctrl+Shift+S (Save As)"
        Write-Host "3. Navigate to: C:\Users\bader\Desktop\CCPRA Project\"
        Write-Host "4. Filename: CCPRA_Customer_Churn_Analytics"
        Write-Host "5. Click Save"
        exit 0
    }
}

Write-Host "Bringing PBI Desktop to foreground..."
[WindowHelper]::ShowWindow($foundHwnd, 9) | Out-Null  # SW_RESTORE
Start-Sleep -Milliseconds 500
[WindowHelper]::SetForegroundWindow($foundHwnd) | Out-Null
Start-Sleep -Milliseconds 500

# Send Ctrl+Shift+S for Save As
Write-Host "Sending Ctrl+Shift+S..."
[System.Windows.Forms.SendKeys]::SendWait("^+s")
Start-Sleep -Seconds 3

# Wait for save dialog, then type the path
$savePath = "C:\Users\bader\Desktop\CCPRA Project\CCPRA_Customer_Churn_Analytics"
[System.Windows.Forms.SendKeys]::SendWait($savePath)
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Seconds 5

Write-Host "Save As command sent. Check if file was created..."
$pbixPath = "C:\Users\bader\Desktop\CCPRA Project\CCPRA_Customer_Churn_Analytics.pbix"
if (Test-Path $pbixPath) {
    $fi = Get-Item $pbixPath
    Write-Host "SUCCESS! File created: $pbixPath ($($fi.Length) bytes)"
} else {
    Write-Host "File was not created. The Save As dialog may need manual interaction."
}
