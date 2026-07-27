#!/usr/bin/env python3
"""Regression tests for ownership-safe PowerShell skill synchronization."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "sync-skills.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
MANAGED_FILE = ".my-skills-managed.json"


@unittest.skipUnless(POWERSHELL, "PowerShell is required for sync script integration tests")
class TestSyncSkillsOwnership(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temporary_directory.name)
        self.target = self.project_root / ".claude" / "skills"
        self.target.mkdir(parents=True)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_sync(self, *arguments, expected_returncode=0):
        command = [
            POWERSHELL,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-ProjectRoot",
            str(self.project_root),
            *arguments,
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, expected_returncode, output)
        return output

    def test_dry_run_reports_add_without_writing(self):
        output = self.run_sync("-DryRun")

        self.assertIn("ADD", output)
        self.assertFalse((self.target / MANAGED_FILE).exists())
        self.assertFalse(any(self.target.iterdir()))

    def test_dry_run_conflict_reports_without_mutating_target(self):
        conflict = self.target / "0-启动"
        conflict.mkdir()
        (conflict / "keep.txt").write_text("unmanaged", encoding="utf-8")

        output = self.run_sync("-DryRun", expected_returncode=1)

        self.assertIn("CONFLICT", output)
        self.assertEqual((conflict / "keep.txt").read_text(encoding="utf-8"), "unmanaged")
        self.assertFalse((self.target / MANAGED_FILE).exists())

    def test_unmanaged_name_conflict_stops_default_sync(self):
        conflict = self.target / "0-启动"
        conflict.mkdir()
        (conflict / "keep.txt").write_text("unmanaged", encoding="utf-8")

        output = self.run_sync(expected_returncode=1)

        self.assertIn("CONFLICT", output)
        self.assertEqual((conflict / "keep.txt").read_text(encoding="utf-8"), "unmanaged")
        self.assertFalse((self.target / MANAGED_FILE).exists())

    def test_take_ownership_updates_only_managed_names_and_preserves_unmanaged(self):
        unmanaged = self.target / "third-party"
        unmanaged.mkdir()
        (unmanaged / "keep.txt").write_text("keep", encoding="utf-8")
        collision = self.target / "0-启动"
        collision.mkdir()
        (collision / "old.txt").write_text("old", encoding="utf-8")

        self.run_sync("-TakeOwnership")

        state = json.loads((self.target / MANAGED_FILE).read_text(encoding="utf-8-sig"))
        self.assertIn("0-启动", state["skills"])
        self.assertTrue((collision / "SKILL.md").is_file())
        self.assertEqual((unmanaged / "keep.txt").read_text(encoding="utf-8"), "keep")

        stale = self.target / "retired-skill"
        stale.mkdir()
        (stale / "obsolete.txt").write_text("obsolete", encoding="utf-8")
        state["skills"].append("retired-skill")
        (self.target / MANAGED_FILE).write_text(json.dumps(state), encoding="utf-8")

        output = self.run_sync()

        self.assertIn("REMOVE MANAGED", output)
        self.assertFalse(stale.exists())
        self.assertEqual((unmanaged / "keep.txt").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
