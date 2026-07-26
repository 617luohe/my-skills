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
$ExpectedCount = $Publication.synchronized_count + $Publication.host_provided_count
if (@($Publication.skills).Count -ne $Publication.synchronized_count) {
    throw "Publication skill count mismatch: expected $($Publication.synchronized_count) synchronized, got $(@($Publication.skills).Count)"
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
        $IsReparsePoint = ($Entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
        if ($DryRun) {
            $TypeLabel = if ($IsReparsePoint) { "junction" } else { "dir" }
            Write-Host "REMOVE [$TypeLabel] $($Entry.FullName)"
        } else {
            if ($IsReparsePoint) {
                # Remove junction itself only, never traverse into target
                Remove-Item -LiteralPath $Entry.FullName -Force
                Write-Host "REMOVE [junction] $($Entry.FullName)"
            } else {
                # Normal directory: safe to recurse
                Remove-Item -LiteralPath $Entry.FullName -Recurse -Force
                Write-Host "REMOVE [dir] $($Entry.FullName)"
            }
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
