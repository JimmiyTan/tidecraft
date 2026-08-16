# Customer demo stop script.
# Stops only a listener whose command line contains customer_demo_server.py.

param(
  [int]$Port = 8765
)

if (-not (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue)) {
  Write-Error "Get-NetTCPConnection is unavailable; refusing an unsafe process stop."
  exit 1
}

$listeners = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalAddress -in @("127.0.0.1", "0.0.0.0", "::1", "::") }

if (-not $listeners) {
  Write-Output "Customer demo is not running on port $Port."
  exit 0
}

$stopped = 0
foreach ($listener in $listeners) {
  $processId = $listener.OwningProcess
  $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
  if (-not $processInfo -or $processInfo.CommandLine -notmatch "customer_demo_server\.py") {
    Write-Error "Port $Port belongs to another process; refusing to stop it."
    exit 1
  }
  Stop-Process -Id $processId -ErrorAction Stop
  $stopped++
}

Write-Output "Customer demo stopped. Process count: $stopped."
