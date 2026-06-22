#Requires -Version 5.1
<#
.SYNOPSIS
  Sync my-skills to project agent skill directories.

.EXAMPLE
  .\my-skills\scripts\sync-skills.ps1
.EXAMPLE
  .\my-skills\scripts\sync-skills.ps1 -DryRun
#>
[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$MySkillsRoot = Split-Path $PSScriptRoot -Parent
$ProjectRoot = Split-Path $MySkillsRoot -Parent
$MapPath = Join-Path $PSScriptRoot "sync-map.json"

if (-not (Test-Path $MapPath)) {
    throw "Missing sync map: $MapPath"
}

$Map = Get-Content -Path $MapPath -Raw -Encoding UTF8 | ConvertFrom-Json

function Copy-SkillTree {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path $Source)) {
        throw "Source not found: $Source"
    }

    if ($DryRun) {
        Write-Host "[dry-run] $Source -> $Destination"
        return
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
    Write-Host "OK $Destination"
}

Write-Host "my-skills : $MySkillsRoot"
Write-Host "project   : $ProjectRoot"
if ($DryRun) { Write-Host "mode      : dry-run" }
Write-Host ""

foreach ($relativeTarget in $Map.agentTargets) {
    $targetRoot = Join-Path $ProjectRoot ($relativeTarget -replace '/', '\')
    if (-not (Test-Path $targetRoot)) {
        Write-Warning "skip missing target: $relativeTarget"
        continue
    }

    Write-Host "==> $relativeTarget"

    foreach ($property in $Map.numbered.PSObject.Properties) {
        $source = Join-Path $MySkillsRoot $property.Name
        $dest = Join-Path $targetRoot $property.Value
        Copy-SkillTree -Source $source -Destination $dest
    }

    foreach ($name in $Map.fullNames) {
        $source = Join-Path $MySkillsRoot $name
        $dest = Join-Path $targetRoot $name
        Copy-SkillTree -Source $source -Destination $dest
    }

    Write-Host ""
}

Write-Host "done."
