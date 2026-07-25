#Requires -Version 5.1
<#
.SYNOPSIS
  Publish the manifest-selected skills as exact mirrors for all known hosts.

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
$ManifestPath = Join-Path $MySkillsRoot "skills-manifest.yaml"
$ManifestTool = Join-Path $PSScriptRoot "skill_manifest.py"
$Targets = @(".claude/skills", ".cursor/skills", ".codex/skills")

if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    throw "Missing manifest: $ManifestPath"
}
if (-not (Test-Path -LiteralPath $ManifestTool -PathType Leaf)) {
    throw "Missing manifest tool: $ManifestTool"
}

$PublicationJson = & python $ManifestTool publication --manifest $ManifestPath
if ($LASTEXITCODE -ne 0) {
    throw "Manifest publication failed with exit code $LASTEXITCODE"
}
$Publication = $PublicationJson | ConvertFrom-Json
if (@($Publication.skills).Count -ne 17) {
    throw "Publication must contain exactly 17 synchronized skills"
}

Write-Host "my-skills : $MySkillsRoot"
Write-Host "project   : $ProjectRoot"
Write-Host "manifest  : $ManifestPath"
Write-Host "version   : $($Publication.repository_version)"
Write-Host "published : $(@($Publication.skills).Count)"
if ($DryRun) { Write-Host "mode      : dry-run" }
Write-Host ""

foreach ($RelativeTarget in $Targets) {
    $TargetRoot = Join-Path $ProjectRoot ($RelativeTarget -replace '/', '\')
    if (-not (Test-Path -LiteralPath $TargetRoot -PathType Container)) {
        Write-Warning "skip missing target: $RelativeTarget"
        continue
    }

    Write-Host "==> $RelativeTarget"
    $ExistingEntries = @(Get-ChildItem -LiteralPath $TargetRoot -Force)
    foreach ($Entry in $ExistingEntries) {
        if ($DryRun) {
            Write-Host "REMOVE $($Entry.FullName)"
        } else {
            Remove-Item -LiteralPath $Entry.FullName -Recurse -Force
            Write-Host "REMOVE $($Entry.FullName)"
        }
    }

    foreach ($Skill in $Publication.skills) {
        $Source = Join-Path $MySkillsRoot $Skill.path
        $Destination = Join-Path $TargetRoot $Skill.name
        if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
            throw "Source not found: $Source"
        }
        if ($DryRun) {
            Write-Host "COPY   $Source -> $Destination"
            continue
        }
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
        Write-Host "COPY   $Source -> $Destination"
    }
    Write-Host ""
}

Write-Host "done."
