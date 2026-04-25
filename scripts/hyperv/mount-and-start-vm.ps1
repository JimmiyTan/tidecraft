# Mount an Ubuntu ISO, start the Hyper-V VM, and open vmconnect.
# Run this script in an elevated Windows PowerShell session.

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$IsoPath,

  [string]$VmName = "lobster-farm-vm"
)

$ErrorActionPreference = "Stop"

function Assert-Admin {
  $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
  )
  if (-not $isAdmin) {
    throw "Please run this script in an elevated Windows PowerShell session."
  }
}

Assert-Admin
Import-Module Hyper-V

if (-not (Test-Path -LiteralPath $IsoPath)) {
  throw "ISO path was not found: $IsoPath"
}

$vm = Get-VM -Name $VmName -ErrorAction SilentlyContinue
if (-not $vm) {
  throw "VM was not found: $VmName"
}

$dvdDrive = Get-VMDvdDrive -VMName $VmName -ErrorAction SilentlyContinue
if (-not $dvdDrive) {
  Add-VMDvdDrive -VMName $VmName | Out-Null
  $dvdDrive = Get-VMDvdDrive -VMName $VmName
}

Set-VMDvdDrive -VMName $VmName -Path $IsoPath

if ($vm.State -ne "Running") {
  Start-VM -Name $VmName | Out-Null
}

Start-Process -FilePath "vmconnect.exe" -ArgumentList @("localhost", $VmName)

$latestVm = Get-VM -Name $VmName
Write-Output "VM mount and start completed."
Write-Output "VM: $VmName"
Write-Output "ISO: $IsoPath"
Write-Output "State: $($latestVm.State)"
