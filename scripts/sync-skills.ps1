#Requires -Version 5.1
<#
.SYNOPSIS
  Publish manifest-selected skills without modifying skills not owned by my-skills.

.DESCRIPTION
  Each target skills root contains .my-skills-managed.json.  The file records the
  skill names managed by this repository during the last successful sync.  Only
  those names may be updated or removed automatically.  Existing untracked skill
  names are conflicts unless -TakeOwnership is explicitly supplied.

.EXAMPLE
  .\my-skills\scripts\sync-skills.ps1
.EXAMPLE
  .\my-skills\scripts\sync-skills.ps1 -DryRun
.EXAMPLE
  .\my-skills\scripts\sync-skills.ps1 -TakeOwnership
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$TakeOwnership,
    [string]$ProjectRoot
)

$ErrorActionPreference = "Stop"

$MySkillsRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path $MySkillsRoot -Parent
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$ManifestPath = Join-Path $MySkillsRoot "skills-manifest.yaml"
$ManifestTool = Join-Path $PSScriptRoot "skill_manifest.py"
$Targets = @(".claude/skills", ".cursor/skills", ".codex/skills")
$ManagedFileName = ".my-skills-managed.json"

function Remove-SkillEntry {
    param([Parameter(Mandatory = $true)][string]$Path)

    $Entry = Get-Item -LiteralPath $Path -Force
    $IsReparsePoint = ($Entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
    if ($IsReparsePoint) {
        Remove-Item -LiteralPath $Path -Force
    } else {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function Get-ManagedSkillNames {
    param([Parameter(Mandatory = $true)][string]$TargetRoot)

    $StatePath = Join-Path $TargetRoot $ManagedFileName
    if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
        return @()
    }

    try {
        $State = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
        $Names = @($State.skills | ForEach-Object { [string]$_ })
        if ($null -eq $State.skills -or @($Names | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count -gt 0) {
            throw "'skills' must be a non-null array of names"
        }
        return @($Names | Select-Object -Unique)
    } catch {
        throw "Invalid managed-skill state file '$StatePath': $($_.Exception.Message)"
    }
}

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
$PublishedSkills = @($Publication.skills)
$PublishedNames = @($PublishedSkills | ForEach-Object { [string]$_.name })
if ($PublishedNames.Count -ne @($PublishedNames | Select-Object -Unique).Count) {
    throw "Manifest publication contains duplicate skill names"
}
if ($PublishedSkills.Count -ne $Publication.synchronized_count) {
    throw "Publication skill count mismatch: expected $($Publication.synchronized_count) synchronized, got $($PublishedSkills.Count)"
}
foreach ($Skill in $PublishedSkills) {
    $Source = Join-Path $MySkillsRoot $Skill.path
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
        throw "Source not found: $Source"
    }
}

Write-Host "my-skills : $MySkillsRoot"
Write-Host "project   : $ProjectRoot"
Write-Host "manifest  : $ManifestPath"
Write-Host "version   : $($Publication.repository_version)"
Write-Host "published : $($PublishedSkills.Count)"
if ($DryRun) { Write-Host "mode      : dry-run" }
if ($TakeOwnership) { Write-Host "ownership: explicit takeover enabled" }
Write-Host ""

# Build every target plan before writing anything. A conflict therefore leaves all
# targets untouched, not merely the target on which it was detected.
$Plans = @()
$Conflicts = @()
foreach ($RelativeTarget in $Targets) {
    $TargetRoot = Join-Path $ProjectRoot ($RelativeTarget -replace '/', '\')
    if (-not (Test-Path -LiteralPath $TargetRoot -PathType Container)) {
        Write-Warning "skip missing target: $RelativeTarget"
        continue
    }

    $ManagedNames = @(Get-ManagedSkillNames $TargetRoot)
    $ManagedLookup = @{}
    foreach ($Name in $ManagedNames) { $ManagedLookup[$Name] = $true }
    $Removals = @($ManagedNames | Where-Object { $_ -notin $PublishedNames })
    $Additions = @()
    $Updates = @()

    foreach ($Skill in $PublishedSkills) {
        $Destination = Join-Path $TargetRoot $Skill.name
        if (Test-Path -LiteralPath $Destination) {
            if ($ManagedLookup.ContainsKey($Skill.name)) {
                $Updates += $Skill
            } elseif ($TakeOwnership) {
                $Updates += $Skill
            } else {
                $Conflicts += [PSCustomObject]@{ Target = $RelativeTarget; Name = $Skill.name; Path = $Destination }
            }
        } else {
            $Additions += $Skill
        }
    }

    $Plans += [PSCustomObject]@{
        RelativeTarget = $RelativeTarget
        TargetRoot = $TargetRoot
        Removals = $Removals
        Additions = $Additions
        Updates = $Updates
    }
}

foreach ($Conflict in $Conflicts) {
    Write-Host "CONFLICT $($Conflict.Target)/$($Conflict.Name) (unmanaged existing skill: $($Conflict.Path))"
}
if ($Conflicts.Count -gt 0) {
    throw "Refusing to overwrite unmanaged skills. Re-run with -TakeOwnership to authorize these takeovers."
}

foreach ($Plan in $Plans) {
    Write-Host "==> $($Plan.RelativeTarget)"
    foreach ($Name in $Plan.Removals) { Write-Host "REMOVE MANAGED $Name" }
    foreach ($Skill in $Plan.Additions) { Write-Host "ADD $($Skill.name)" }
    foreach ($Skill in $Plan.Updates) { Write-Host "UPDATE $($Skill.name)" }

    if ($DryRun) {
        Write-Host ""
        continue
    }

    # Copy all sources to a private sibling staging directory before replacing any
    # managed destination. The ownership file is moved into place only after every
    # copy/replacement succeeds.
    $StagingRoot = Join-Path $Plan.TargetRoot (".my-skills-staging-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $StagingRoot | Out-Null
    try {
        foreach ($Skill in ($Plan.Additions + $Plan.Updates)) {
            $Source = Join-Path $MySkillsRoot $Skill.path
            $StagedDestination = Join-Path $StagingRoot $Skill.name
            New-Item -ItemType Directory -Path (Split-Path $StagedDestination -Parent) -Force | Out-Null
            Copy-Item -LiteralPath $Source -Destination $StagedDestination -Recurse -Force
        }

        foreach ($Name in $Plan.Removals) {
            $Destination = Join-Path $Plan.TargetRoot $Name
            if (Test-Path -LiteralPath $Destination) { Remove-SkillEntry $Destination }
        }
        foreach ($Skill in ($Plan.Additions + $Plan.Updates)) {
            $Destination = Join-Path $Plan.TargetRoot $Skill.name
            if (Test-Path -LiteralPath $Destination) { Remove-SkillEntry $Destination }
            New-Item -ItemType Directory -Path (Split-Path $Destination -Parent) -Force | Out-Null
            Move-Item -LiteralPath (Join-Path $StagingRoot $Skill.name) -Destination $Destination
        }

        $State = [PSCustomObject]@{ schema_version = 1; skills = @($PublishedNames | Sort-Object) }
        $TemporaryState = Join-Path $Plan.TargetRoot (".my-skills-managed-" + [guid]::NewGuid().ToString("N") + ".tmp")
        $State | ConvertTo-Json | Set-Content -LiteralPath $TemporaryState -Encoding UTF8
        $StatePath = Join-Path $Plan.TargetRoot $ManagedFileName
        if (Test-Path -LiteralPath $StatePath) { Remove-Item -LiteralPath $StatePath -Force }
        Move-Item -LiteralPath $TemporaryState -Destination $StatePath
    } finally {
        if (Test-Path -LiteralPath $StagingRoot) { Remove-Item -LiteralPath $StagingRoot -Recurse -Force }
    }
    Write-Host ""
}

Write-Host "done."
