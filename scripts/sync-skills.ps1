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
    [string]$ProjectRoot,
    [ValidateRange(1, [int]::MaxValue)]
    [int]$FailAfterReplacement = 0
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

function Test-SafeSkillPath {
    param([object]$Value)

    if ($Value -isnot [string] -or [string]::IsNullOrWhiteSpace($Value) -or
        [System.IO.Path]::IsPathRooted($Value) -or $Value -match '^[A-Za-z]:' -or
        $Value.StartsWith('\\') -or $Value.Contains('\')) { return $false }
    $Parts = $Value.Split('/')
    return $Parts.Count -gt 0 -and @($Parts | Where-Object {
        [string]::IsNullOrWhiteSpace($_) -or $_ -eq '.' -or $_ -eq '..' -or
        $_.IndexOfAny([System.IO.Path]::GetInvalidFileNameChars()) -ge 0
    }).Count -eq 0
}

function Get-ContainedPath {
    param([string]$Base, [string]$Relative, [string]$Description)

    if (-not (Test-SafeSkillPath $Relative)) { throw "Unsafe $Description path: '$Relative'" }
    $FullBase = [System.IO.Path]::GetFullPath($Base).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $FullPath = [System.IO.Path]::GetFullPath((Join-Path $FullBase ($Relative -replace '/', '\')))
    if (-not $FullPath.StartsWith($FullBase + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Description path escapes its root: '$Relative'"
    }
    return $FullPath
}

function Assert-NoReparsePointBoundary {
    param([string]$Path, [string]$Boundary, [string]$Description)

    $FullBoundary = [System.IO.Path]::GetFullPath($Boundary)
    $FullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $FullPath.StartsWith($FullBoundary, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Description is outside boundary: $Path"
    }
    $Current = $FullBoundary
    if ((Get-Item -LiteralPath $Current -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        throw "$Description boundary is a reparse point: $Current"
    }
    $Suffix = $FullPath.Substring($FullBoundary.Length).TrimStart('\', '/')
    foreach ($Part in $Suffix -split '[\\/]' | Where-Object { $_ }) {
        $Current = Join-Path $Current $Part
        if (Test-Path -LiteralPath $Current) {
            $Entry = Get-Item -LiteralPath $Current -Force
            if (($Entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "$Description contains a reparse point: $Current"
            }
        }
    }
}

function Assert-DestinationAncestors {
    param([string]$TargetRoot, [string]$SkillPath, [string]$RelativeTarget)

    $Current = $TargetRoot
    $Parts = $SkillPath.Split('/')
    for ($Index = 0; $Index -lt $Parts.Count - 1; $Index++) {
        $Current = Join-Path $Current $Parts[$Index]
        if (Test-Path -LiteralPath $Current) {
            $Entry = Get-Item -LiteralPath $Current -Force
            if (-not $Entry.PSIsContainer -or (($Entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
                $script:Conflicts += [PSCustomObject]@{ Target = $RelativeTarget; Name = $SkillPath; Path = $Current; Reason = 'unsafe ancestor' }
            }
        }
    }
}

function Remove-SkillEntry {
    param([Parameter(Mandatory = $true)][string]$Path)
    $Entry = Get-Item -LiteralPath $Path -Force
    if (($Entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Refusing to remove reparse point: $Path" }
    Remove-Item -LiteralPath $Path -Recurse -Force
}

function Get-ManagedSkillNames {
    param([Parameter(Mandatory = $true)][string]$TargetRoot)

    $StatePath = Join-Path $TargetRoot $ManagedFileName
    if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
        return @()
    }

    try {
        $State = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
        if ($State.schema_version -ne 1 -or $null -eq $State.skills -or $State.skills -is [string] -or $State.skills -isnot [System.Collections.IEnumerable]) {
            throw "'schema_version' must be 1 and 'skills' must be an array of names"
        }
        $Names = @($State.skills)
        if (@($Names | Where-Object { $_ -isnot [string] -or -not (Test-SafeSkillPath $_) }).Count -gt 0) {
            throw "'skills' must contain safe, non-empty relative directory paths"
        }
        if ($Names.Count -ne @($Names | Select-Object -Unique).Count) {
            throw "'skills' must not contain duplicate names"
        }
        return $Names
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
    if ($Skill.name -isnot [string] -or $Skill.path -isnot [string] -or
        -not (Test-SafeSkillPath $Skill.name) -or -not (Test-SafeSkillPath $Skill.path) -or
        $Skill.name -ne $Skill.path) {
        throw "Manifest publication contains unsafe name or path"
    }
    $Source = Get-ContainedPath $MySkillsRoot $Skill.path 'source'
    Assert-NoReparsePointBoundary $Source $MySkillsRoot 'source'
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
        throw "Source not found: $Source"
    }
    $Skill | Add-Member -NotePropertyName SourcePath -NotePropertyValue $Source
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
$CompletedTransactions = @()
$ReplacementCount = 0
foreach ($RelativeTarget in $Targets) {
    $TargetRoot = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot ($RelativeTarget -replace '/', '\')))
    if (-not (Test-Path -LiteralPath $TargetRoot -PathType Container)) {
        Write-Warning "skip missing target: $RelativeTarget"
        continue
    }

    Assert-NoReparsePointBoundary $TargetRoot $ProjectRoot "target $RelativeTarget"
    $ManagedNames = @(Get-ManagedSkillNames $TargetRoot)
    $ManagedLookup = @{}
    foreach ($Name in $ManagedNames) { $ManagedLookup[$Name] = $true }
    $Removals = @($ManagedNames | Where-Object { $_ -notin $PublishedNames })
    $Additions = @()
    $Updates = @()

    foreach ($Skill in $PublishedSkills) {
        $Destination = Get-ContainedPath $TargetRoot $Skill.name 'destination'
        Assert-DestinationAncestors $TargetRoot $Skill.name $RelativeTarget
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

# Prepare every target's replacement tree before moving any live content.  A copy
# failure therefore cannot leave an earlier host partially published.
if (-not $DryRun) {
    try {
        foreach ($Plan in $Plans) {
            $TransactionId = [guid]::NewGuid().ToString("N")
            $Plan | Add-Member -NotePropertyName TransactionId -NotePropertyValue $TransactionId
            $Plan | Add-Member -NotePropertyName StagingRoot -NotePropertyValue (Join-Path $Plan.TargetRoot (".my-skills-staging-" + $TransactionId))
            $Plan | Add-Member -NotePropertyName BackupRoot -NotePropertyValue (Join-Path $Plan.TargetRoot (".my-skills-backup-" + $TransactionId))
            New-Item -ItemType Directory -Path $Plan.StagingRoot | Out-Null
            foreach ($Skill in ($Plan.Additions + $Plan.Updates)) {
                $StagedDestination = Get-ContainedPath $Plan.StagingRoot $Skill.name 'staging destination'
                New-Item -ItemType Directory -Path (Split-Path $StagedDestination -Parent) -Force | Out-Null
                Copy-Item -LiteralPath $Skill.SourcePath -Destination $StagedDestination -Recurse -Force
            }
        }
    } catch {
        foreach ($PreparedPlan in $Plans) {
            if ($PreparedPlan.PSObject.Properties['StagingRoot'] -and (Test-Path -LiteralPath $PreparedPlan.StagingRoot)) {
                Remove-Item -LiteralPath $PreparedPlan.StagingRoot -Recurse -Force
            }
        }
        throw "Sync preparation failed: $($_.Exception.Message)"
    }
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

    # A target is one exception-safe transaction.  All source copies complete before
    # mutation; existing managed entries and state are renamed to a private sibling
    # backup on the same volume before staged replacements are installed.
    $TransactionId = $Plan.TransactionId
    $StagingRoot = $Plan.StagingRoot
    $BackupRoot = $Plan.BackupRoot
    $TemporaryState = $null
    $Backups = @()
    $Installed = @()
    $Committed = $false
    try {
        New-Item -ItemType Directory -Path $BackupRoot | Out-Null
        $StatePath = Join-Path $Plan.TargetRoot $ManagedFileName
        $OldPaths = @($Plan.Removals) + @($Plan.Updates | ForEach-Object { $_.name }) + @($ManagedFileName)
        foreach ($Name in ($OldPaths | Select-Object -Unique)) {
            $Destination = Get-ContainedPath $Plan.TargetRoot $Name 'backup destination'
            Assert-NoReparsePointBoundary $Destination $Plan.TargetRoot 'backup destination'
            if (Test-Path -LiteralPath $Destination) {
                $BackupPath = Join-Path $BackupRoot $Name
                New-Item -ItemType Directory -Path (Split-Path $BackupPath -Parent) -Force | Out-Null
                Move-Item -LiteralPath $Destination -Destination $BackupPath
                $Backups += [PSCustomObject]@{ Destination = $Destination; Backup = $BackupPath }
            }
        }

        foreach ($Skill in ($Plan.Additions + $Plan.Updates)) {
            $Destination = Get-ContainedPath $Plan.TargetRoot $Skill.name 'installation destination'
            Assert-NoReparsePointBoundary (Split-Path $Destination -Parent) $Plan.TargetRoot 'installation parent'
            New-Item -ItemType Directory -Path (Split-Path $Destination -Parent) -Force | Out-Null
            Move-Item -LiteralPath (Join-Path $StagingRoot $Skill.name) -Destination $Destination
            $Installed += $Destination
            $ReplacementCount++
            if ($FailAfterReplacement -gt 0 -and $ReplacementCount -ge $FailAfterReplacement) {
                throw "Injected failure after replacement $ReplacementCount"
            }
        }

        $State = [PSCustomObject]@{ schema_version = 1; skills = @($PublishedNames | Sort-Object) }
        $TemporaryState = Join-Path $Plan.TargetRoot (".my-skills-managed-" + $TransactionId + ".tmp")
        $State | ConvertTo-Json | Set-Content -LiteralPath $TemporaryState -Encoding UTF8
        Move-Item -LiteralPath $TemporaryState -Destination $StatePath
        $Installed += $StatePath
        $TemporaryState = $null
        $Committed = $true
        $CompletedTransactions += [PSCustomObject]@{ Target = $Plan.TargetRoot; Backups = $Backups; Installed = $Installed; BackupRoot = $BackupRoot }
    } catch {
        $Failure = $_
        $RollbackErrors = @()
        foreach ($Destination in $Installed) {
            try { if (Test-Path -LiteralPath $Destination) { Remove-SkillEntry $Destination } } catch { $RollbackErrors += "remove '$Destination': $($_.Exception.Message)" }
        }
        if ($null -ne $TemporaryState -and (Test-Path -LiteralPath $TemporaryState)) {
            try { Remove-Item -LiteralPath $TemporaryState -Force } catch { $RollbackErrors += "remove temporary state: $($_.Exception.Message)" }
        }
        $BackupsToRestore = @($Backups)
        [array]::Reverse($BackupsToRestore)
        foreach ($Backup in $BackupsToRestore) {
            try { Move-Item -LiteralPath $Backup.Backup -Destination $Backup.Destination } catch { $RollbackErrors += "restore '$($Backup.Destination)': $($_.Exception.Message)" }
        }
        foreach ($Completed in @($CompletedTransactions | Sort-Object { $_.Target } -Descending)) {
            foreach ($InstalledPath in $Completed.Installed) {
                try { if (Test-Path -LiteralPath $InstalledPath) { Remove-SkillEntry $InstalledPath } } catch { $RollbackErrors += "global remove '$InstalledPath': $($_.Exception.Message)" }
            }
            $CompletedBackups = @($Completed.Backups)
            [array]::Reverse($CompletedBackups)
            foreach ($CompletedBackup in $CompletedBackups) {
                try { Move-Item -LiteralPath $CompletedBackup.Backup -Destination $CompletedBackup.Destination } catch { $RollbackErrors += "global restore '$($CompletedBackup.Destination)': $($_.Exception.Message)" }
            }
        }
        if ($RollbackErrors.Count -gt 0) {
            throw "Sync failed: $($Failure.Exception.Message). Rollback also failed: $($RollbackErrors -join '; '). Backup retained at '$BackupRoot'."
        }
        throw "Sync failed: $($Failure.Exception.Message). Rollback completed."
    } finally {
        if (Test-Path -LiteralPath $StagingRoot) { Remove-Item -LiteralPath $StagingRoot -Recurse -Force }
        if (-not $Committed -and (Test-Path -LiteralPath $BackupRoot) -and -not (Get-ChildItem -LiteralPath $BackupRoot -Force | Select-Object -First 1)) { Remove-Item -LiteralPath $BackupRoot -Force }
    }
    Write-Host ""
}

foreach ($Completed in $CompletedTransactions) {
    if (Test-Path -LiteralPath $Completed.BackupRoot) { Remove-Item -LiteralPath $Completed.BackupRoot -Recurse -Force }
}

Write-Host "done."
