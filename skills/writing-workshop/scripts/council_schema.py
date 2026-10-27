"""Shared schema constants for writing-workshop council scripts."""

from __future__ import annotations

import re


MAX_ROUNDS = 10
MAX_ITERATIONS_PER_ROUND = 10
DEFAULT_ITERATIONS_PER_ROUND = 10
DEFAULT_PROCESS_DIRECTORY = "council"
ROUND_RE = re.compile(r"round-(\d+)$")
ITERATION_RE = re.compile(r"iteration-(\d+)$")

ITERATION_FILENAMES = (
    "draft.md",
    "review.md",
    "revision.md",
    "decision.md",
    "coverage.yaml",
    "input-snapshot.yaml",
)
ROUND_GATE_FILENAMES = ("round-summary.md", "user-decision.md")
ROUND_FILENAMES = ITERATION_FILENAMES + ROUND_GATE_FILENAMES

ALLOWED_STATUS = frozenset(
    {
        "drafting",
        "reviewing",
        "revising",
        "approval",
        "awaiting_user_decision",
        "blocked",
        "stopped_by_user",
        "published",
    }
)
PATH_SOURCES = frozenset({"user", "external_contract", "default"})
PROCESS_PATH_SOURCES = frozenset({"user", "default"})
ROUND_GATES = frozenset({"none", "awaiting_user_decision", "continue", "stop", "blocked"})
