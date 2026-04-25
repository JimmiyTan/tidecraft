# Create the Hyper-V VM for lobster-farm.
# This script only creates the VM, VHD, network binding, and optional ISO mount.
# Run this script in an elevated Windows PowerShell session.

[CmdletBinding()]
param(
  [string]$VmName = "lobster-farm-vm",
  [string]$SwitchName = "Default Switch",
  [string]$IsoPath = ""
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

function Get-StartupMemoryBytes {
  $os = Get-CimInstance Win32_OperatingSystem
  $freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
  if ($freeGB -ge 12) {
    return 8GB
  }
  return 6GB
}

Assert-Admin
Import-Module Hyper-V

if (Get-VM -Name $VmName -ErrorAction SilentlyContinue) {
  throw "VM already exists: $VmName"
}

$switch = Get-VMSwitch -Name $SwitchName -ErrorAction SilentlyContinue
if (-not $switch) {
  throw "Hyper-V switch was not found: $SwitchName"
}

$startupMemoryBytes = Get-StartupMemoryBytes
$vhdSizeBytes = 60GB
$vmHost = Get-VMHost
$vmRootPath = $vmHost.VirtualMachinePath
$vhdRootPath = $vmHost.VirtualHardDiskPath
$vhdPath = Join-Path $vhdRootPath ($VmName + ".vhdx")

if (-not (Test-Path -LiteralPath $vmRootPath)) {
  New-Item -ItemType Directory -Force -Path $vmRootPath | Out-Null
}
if (-not (Test-Path -LiteralPath $vhdRootPath)) {
  New-Item -ItemType Directory -Force -Path $vhdRootPath | Out-Null
}

$null = New-VM `
  -Name $VmName `
  -Path $vmRootPath `
  -Generation 2 `
  -MemoryStartupBytes $startupMemoryBytes `
  -NewVHDPath $vhdPath `
  -NewVHDSizeBytes $vhdSizeBytes `
  -SwitchName $SwitchName

Set-VM -Name $VmName -ProcessorCount 4
Set-VMMemory -VMName $VmName -DynamicMemoryEnabled $true -MinimumBytes 4GB -StartupBytes $startupMemoryBytes -MaximumBytes 8GB
Set-VMFirmware -VMName $VmName -EnableSecureBoot On -SecureBootTemplate "MicrosoftUEFICertificateAuthority"

$dvdDrive = Get-VMDvdDrive -VMName $VmName -ErrorAction SilentlyContinue
if (-not $dvdDrive) {
  Add-VMDvdDrive -VMName $VmName | Out-Null
  $dvdDrive = Get-VMDvdDrive -VMName $VmName
}

if ($IsoPath) {
  if (-not (Test-Path -LiteralPath $IsoPath)) {
    throw "ISO path was not found: $IsoPath"
  }
  Set-VMDvdDrive -VMName $VmName -Path $IsoPath
}

$vmObject = Get-VM -Name $VmName
$hardDiskDrive = Get-VMHardDiskDrive -VMName $VmName
$bootDvdDrive = Get-VMDvdDrive -VMName $VmName
if ($bootDvdDrive) {
  Set-VMFirmware -VMName $VmName -FirstBootDevice $bootDvdDrive
}

$isoStatus = "not mounted"
if (-not [string]::IsNullOrWhiteSpace($IsoPath)) {
  $isoStatus = $IsoPath
}

Write-Output "VM creation completed."
Write-Output "VM Name: $VmName"
Write-Output "Generation: $($vmObject.Generation)"
Write-Output "CPU: $($vmObject.ProcessorCount) vCPU"
Write-Output "Startup Memory: $([math]::Round($vmObject.MemoryStartup / 1GB, 2)) GB"
Write-Output "Dynamic Memory: enabled (min 4GB, max 8GB)"
Write-Output "VHD Path: $($hardDiskDrive.Path)"
Write-Output "Switch: $SwitchName"
Write-Output "ISO: $isoStatus"
