$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Loop Adventure.lnk"
$runScript = Join-Path $projectRoot "scripts\run.ps1"
$iconTarget = Join-Path $projectRoot "release\Loop Adventure\Loop Adventure.exe"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
if (Test-Path $iconTarget) {
  $shortcut.TargetPath = $iconTarget
  $shortcut.Arguments = ""
} else {
  $shortcut.TargetPath = "powershell.exe"
  $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$runScript`""
}
$shortcut.WorkingDirectory = $projectRoot
$shortcut.Description = "Abrir Loop Adventure"

if (Test-Path $iconTarget) {
  $shortcut.IconLocation = $iconTarget
} else {
  $shortcut.IconLocation = "powershell.exe,0"
}

$shortcut.Save()

Write-Host "Atalho criado em: $shortcutPath"
