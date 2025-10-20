$FilePath = Join-Path -Path $PSScriptRoot -ChildPath "AudioDeviceCmdlets.dll"
New-Item "$($profile | split-path)\Modules\AudioDeviceCmdlets" -Type directory -Force
Copy-Item $FilePath "$($profile | split-path)\Modules\AudioDeviceCmdlets\AudioDeviceCmdlets.dll"
Set-Location "$($profile | Split-Path)\Modules\AudioDeviceCmdlets"
Get-ChildItem | Unblock-File
Import-Module AudioDeviceCmdlets