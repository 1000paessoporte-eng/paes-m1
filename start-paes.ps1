# Levanta PAES M1 para toda la LAN: Postgres (Docker) + API (:8000) + Web (:3000).
# Uso:  powershell -ExecutionPolicy Bypass -File C:\Users\matmi\paes-m1\start-paes.ps1

$repo = $PSScriptRoot

Write-Host "1/3 Postgres..." -ForegroundColor Cyan
docker start paes-postgres | Out-Null
do { Start-Sleep -Seconds 1 } until (docker exec paes-postgres pg_isready -U paes -d paes_m1 2>$null)

Write-Host "2/3 API en 0.0.0.0:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
  '-NoExit', '-Command',
  "Set-Location '$repo\apps\api'; python -m uv run uvicorn paes_api.main:app --host 0.0.0.0 --port 8000"
)

Write-Host "3/3 Web en 0.0.0.0:3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
  '-NoExit', '-Command',
  "Set-Location '$repo\apps\web'; pnpm exec next start -H 0.0.0.0 -p 3000"
)

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.InterfaceAlias -eq 'Wi-Fi' } |
  Select-Object -First 1).IPAddress

Write-Host ""
Write-Host "Listo. Comparte esta direccion en la red:  http://${ip}:3000" -ForegroundColor Green
Write-Host "Si cambiaste de red y la IP no coincide, revisa con: ipconfig" -ForegroundColor DarkGray
