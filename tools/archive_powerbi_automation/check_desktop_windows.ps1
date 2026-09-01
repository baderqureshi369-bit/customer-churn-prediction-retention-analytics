Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class WinEnum {
    [DllImport("user32.dll")]
    public static extern bool EnumDesktopWindows(IntPtr hDesktop, EnumWindowsProc lpfn, IntPtr lParam);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern int GetClassName(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@

$list = New-Object System.Collections.ArrayList

[WinEnum]::EnumDesktopWindows([IntPtr]::Zero, {
    param($hwnd, $lparam)
    $pid = 0
    [WinEnum]::GetWindowThreadProcessId($hwnd, [ref]$pid) | Out-Null
    $sbText = New-Object System.Text.StringBuilder 512
    [WinEnum]::GetWindowText($hwnd, $sbText, $sbText.Capacity) | Out-Null
    $sbClass = New-Object System.Text.StringBuilder 512
    [WinEnum]::GetClassName($hwnd, $sbClass, $sbClass.Capacity) | Out-Null
    $visible = [WinEnum]::IsWindowVisible($hwnd)

    $text = $sbText.ToString()
    $class = $sbClass.ToString()

    if ($text -match "Power BI" -or $pid -eq 17016 -or $text -match "CCPRA") {
        Write-Host "HWND: $hwnd | PID: $pid | Vis: $visible | Class: $class | Title: '$text'"
    }
    return $true
}, [IntPtr]::Zero) | Out-Null
