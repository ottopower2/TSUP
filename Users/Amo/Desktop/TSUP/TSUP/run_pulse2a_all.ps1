$Python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Python 3.12 wurde nicht gefunden: $Python"
    exit 1
}

& $Python "$PSScriptRoot\pulse2a_all.py"
exit $LASTEXITCODE
