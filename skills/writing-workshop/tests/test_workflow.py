"""End-to-end invariants for intake gating and role-context minimization."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"


class WorkflowTest(unittest.TestCase):
    def run_script(self, name: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            cwd=SKILL,
            text=True,
            capture_output=True,
            check=check,
        )

    def test_intake_gate_confirmation_and_role_packets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            council = root / "council"
            self.run_script(
                "init_council.py",
                "--council-path", str(council),
                "--document-slug", "demo-prd",
                "--title", "Demo PRD",
                "--target-path", str(root / "final.md"),
                "--purpose", "demo",
                "--audience", "team",
            )
            self.assertFalse((council / "rounds").exists())
            self.run_script("validate_council.py", str(council))

            brief = root / "brief.md"
            brief.write_text("为移动端设计结算功能的产品需求文档，供产品、设计和研发评审。\n", encoding="utf-8")
            self.run_script("route_intake.py", "--council-dir", str(council), "--brief-file", str(brief))
            pending = json.loads((council / "pending-user-input.json").read_text(encoding="utf-8"))
            self.assertEqual(pending["document_candidates"][0]["id"], "product.prd")
            self.assertIn("产品需求", (council / "user-brief.md").read_text(encoding="utf-8"))

            self.run_script(
                "confirm_intake.py", "--council-dir", str(council),
                "--document-pack", "product.prd", "--style-or-channel", "内部 PRD",
                "--role-combination-id", "product.prd-roles-1", "--source", "cli-resume",
            )
            self.assertTrue((council / "rounds" / "round-01" / "iterations" / "iteration-01").is_dir())
            self.assertFalse((council / "pending-user-input.json").exists())
            self.run_script("validate_council.py", str(council))

            local = root / "local"
            self.run_script(
                "manage_fragments.py", "--local-root", str(local), "add-candidate",
                "--id", "user.role.product-focus", "--kind", "role", "--applies-to", "product-manager",
                "--change", "State a measurable product outcome.", "--acceptance", "Every goal has a measure.",
            )
            self.run_script("manage_fragments.py", "--local-root", str(local), "activate", "--id", "user.role.product-focus")
            writer = self.run_script("resolve_context.py", "--council-dir", str(council), "--role", "writer", "--local-root", str(local))
            writer_packet = json.loads(Path(writer.stdout.strip()).read_text(encoding="utf-8"))
            writer_paths = [item["path"] for item in writer_packet["allowed_artifacts"]]
            self.assertFalse(any(path.endswith("source-index.md") for path in writer_paths))
            self.assertEqual(writer_packet["active_local_fragments"][0]["fragment"]["id"], "user.role.product-focus")

            reviewer = self.run_script("resolve_context.py", "--council-dir", str(council), "--role", "reviewer", "--source-id", "S-001")
            reviewer_packet = json.loads(Path(reviewer.stdout.strip()).read_text(encoding="utf-8"))
            self.assertEqual(reviewer_packet["source_subset"], ["| S-001 | `[TBD]` | `[TBD]` | `[TBD]` |"])
            self.assertFalse(any(item["path"].endswith("source-index.md") for item in reviewer_packet["allowed_artifacts"]))

            checker = self.run_script(
                "resolve_context.py", "--council-dir", str(council), "--role", "checker",
                "--full-context-reason", "safety-or-compliance",
            )
            checker_packet = json.loads(Path(checker.stdout.strip()).read_text(encoding="utf-8"))
            self.assertEqual(checker_packet["context_policy"], "full-exception")
            self.assertTrue(any(item["path"].endswith("source-index.md") for item in checker_packet["allowed_artifacts"]))
            self.run_script("validate_council.py", str(council))


if __name__ == "__main__":
    unittest.main()
