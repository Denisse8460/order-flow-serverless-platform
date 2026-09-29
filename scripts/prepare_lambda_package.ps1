$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot

$packageDirectory = Join-Path `
    $projectRoot `
    ".lambda-package"

if (Test-Path $packageDirectory) {
    Remove-Item `
        $packageDirectory `
        -Recurse `
        -Force
}

New-Item `
    -ItemType Directory `
    -Path $packageDirectory `
    | Out-Null

Copy-Item `
    -Path (Join-Path $projectRoot "src") `
    -Destination (Join-Path $packageDirectory "src") `
    -Recurse

Copy-Item `
    -Path (Join-Path $projectRoot "requirements-lambda.txt") `
    -Destination (Join-Path $packageDirectory "requirements.txt")

Write-Host "Lambda package prepared successfully."