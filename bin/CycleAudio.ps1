param(
    [ValidateSet("Next","Prev")]
    [string]$Direction = "Next"
)

# Import required modules
Import-Module AudioDeviceCmdlets

# Get all playback devices
$devices = Get-AudioDevice -List | Where-Object { $_.Type -eq 'Playback' } | Sort-Object Index

# Get the current playback device
$current = Get-AudioDevice -Playback

# Find current device index in the list
$indices = $devices | ForEach-Object { $_.Index }
$currentIndex = [array]::IndexOf($indices, $current.Index)

# Calculate next or previous index
if ($Direction -eq "Next") {
    $newIndex = ($currentIndex + 1) % $devices.Count
}
else {
    $newIndex = $currentIndex - 1
    if ($newIndex -lt 0) { $newIndex = $devices.Count - 1 }
}

# Switch default device
$newDevice = $devices[$newIndex]
Set-AudioDevice -Index $newDevice.Index

#Save device name to file
$filePath = Join-Path -Path $PSScriptRoot -ChildPath "Current_Device.txt"
$newDevice.Name | Set-Content -Path $filePath
