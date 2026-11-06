# Reversible local prerequisites check; never changes other repositories.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$env:PYTHONPATH = (Join-Path $PSScriptRoot 'src')
& py -3 -m gf_observatory doctor
if ($LASTEXITCODE -ne 0) { throw 'Configuration invalide.' }
& py -3 -m unittest discover -s tests -q
if ($LASTEXITCODE -ne 0) { throw 'Tests unitaires en échec.' }
Write-Host 'Installation locale contrôlée. Lancer Lancer_GF_Observatory.bat.'
