Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class WinAPI {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
}
"@

[WinAPI]::EnumWindows({
    param($hwnd, $lparam)
    $pid = 0
    [WinAPI]::GetWindowThreadProcessId($hwnd, [ref]$pid) | Out-Null
    if ($pid -eq 17016) {
        $sb = New-Object System.Text.StringBuilder 512
        [WinAPI]::GetWindowText($hwnd, $sb, $sb.Capacity) | Out-Null
        $visible = [WinAPI]::IsWindowVisible($hwnd)
        $title = $sb.ToString()
        if ($title.Length -gt 0 -or $visible) {
            Write-Host "HWND: $hwnd | PID: $pid | Visible: $visible | Title: '$title'"
        }
    }
    return $true
}, [IntPtr]::Zero) | Out-Null
