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
        result = subprocess.run(
            command, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False
        )
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

    def test_failure_during_replacement_restores_old_content_and_state(self):
        managed = self.target / "0-启动"
        managed.mkdir()
        (managed / "old.txt").write_bytes(b"old managed content\x00")
        retired = self.target / "retired-skill"
        retired.mkdir()
        (retired / "obsolete.txt").write_bytes(b"obsolete\x00content")
        third_party = self.target / "third-party"
        third_party.mkdir()
        (third_party / "keep.txt").write_bytes(b"third-party\x00content")
        old_state = ('{"schema_version": 1, "skills": ["0-启动", "retired-skill"]}\r\n').encode("utf-8")
        (self.target / MANAGED_FILE).write_bytes(old_state)

        output = self.run_sync("-TakeOwnership", "-FailAfterReplacement", "1", expected_returncode=1)

        self.assertIn("rollback", output.lower())
        self.assertEqual((managed / "old.txt").read_bytes(), b"old managed content\x00")
        self.assertEqual((retired / "obsolete.txt").read_bytes(), b"obsolete\x00content")
        self.assertEqual((third_party / "keep.txt").read_bytes(), b"third-party\x00content")
        self.assertEqual((self.target / MANAGED_FILE).read_bytes(), old_state)
        self.assertFalse((managed / "SKILL.md").exists())
        self.assertFalse(any(self.target.glob(".my-skills-staging-*")))
        self.assertFalse(any(self.target.glob(".my-skills-backup-*")))

    def test_rejects_unsafe_state_names_without_writing(self):
        victim = self.project_root / "victim"
        victim.mkdir()
        (victim / "keep.txt").write_text("keep", encoding="utf-8")
        for name in ("..", "../../victim"):
            with self.subTest(name=name):
                (self.target / MANAGED_FILE).write_text(
                    json.dumps({"schema_version": 1, "skills": [name]}), encoding="utf-8"
                )
                output = self.run_sync(expected_returncode=1)
                self.assertIn("Invalid managed-skill state", output)
                self.assertEqual((victim / "keep.txt").read_text(encoding="utf-8"), "keep")

    def test_rejects_non_array_or_wrong_schema_state(self):
        for state in (
            {"schema_version": 1, "skills": "0-启动"},
            {"schema_version": 2, "skills": ["0-启动"]},
        ):
            with self.subTest(state=state):
                (self.target / MANAGED_FILE).write_text(json.dumps(state), encoding="utf-8")
                output = self.run_sync(expected_returncode=1)
                self.assertIn("Invalid managed-skill state", output)

    def test_nested_ancestor_file_conflict_prevents_all_target_writes(self):
        second_target = self.project_root / ".cursor" / "skills"
        second_target.mkdir(parents=True)
        (second_target / "vocabulary").write_text("not a directory", encoding="utf-8")

        output = self.run_sync(expected_returncode=1)

        self.assertIn("CONFLICT", output)
        self.assertFalse((self.target / MANAGED_FILE).exists())
        self.assertFalse(any(self.target.iterdir()))

    def test_second_target_failure_rolls_back_first_target(self):
        second_target = self.project_root / ".cursor" / "skills"
        second_target.mkdir(parents=True)
        old_skill = self.target / "0-启动"
        old_skill.mkdir()
        (old_skill / "old.txt").write_text("old", encoding="utf-8")
        old_state = json.dumps({"schema_version": 1, "skills": ["0-启动"]})
        (self.target / MANAGED_FILE).write_text(old_state, encoding="utf-8")

        output = self.run_sync("-FailAfterReplacement", "2", expected_returncode=1)

        self.assertIn("rollback", output.lower())
        self.assertEqual((old_skill / "old.txt").read_text(encoding="utf-8"), "old")
        self.assertEqual((self.target / MANAGED_FILE).read_text(encoding="utf-8"), old_state)

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
