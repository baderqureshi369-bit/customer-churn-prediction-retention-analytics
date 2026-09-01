$path = "C:\Users\bader\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_e00317cc-e952-4283-83d0-8025c8c299fd"
Get-ChildItem -Recurse -Path $path | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
