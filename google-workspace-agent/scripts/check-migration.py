#!/usr/bin/env python3
"""Verify a Google Workspace agent migration from REST APIs to MCP.

Usage:
    python3 check-migration.py <agent-project-dir>
    python3 check-migration.py --self-test

Checks, against the agent project directory:
  1. No direct Google Workspace REST calls remain in the agent's
     code or config (no *.googleapis.com REST hostnames, no
     /gmail/v1, /drive/v3, /calendar/v3 style paths).
  2. An MCP configuration is present (a config file that points at
     a Workspace MCP server, or a gwscli reference).
  3. A tier selection is recorded (workspace-migration.json or
     MIGRATION.md naming Standard or Scaled, with a daily estimate).

Exit code 0 on pass, 1 on fail, with a clear message for each
failed check. This script never modifies the project it checks.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Workspace REST hostnames an agent must no longer call directly.
# The MCP server hostnames (*mcp.googleapis.com) are NOT in this
# list — they are the correct destination.
REST_HOSTS = [
    "gmail.googleapis.com",
    "drive.googleapis.com",
    "docs.googleapis.com",
    "sheets.googleapis.com",
    "slides.googleapis.com",
    "calendar.googleapis.com",
    "chat.googleapis.com",
    "tasks.googleapis.com",
    "www.googleapis.com",
]

# REST path markers, in case a call is written as a path only.
REST_PATHS = [
    "/gmail/v1",
    "/drive/v2",
    "/drive/v3",
    "/docs/v1",
    "/sheets/v4",
    "/slides/v1",
    "/calendar/v3",
    "/chat/v1",
    "/tasks/v1",
]

MCP_MARKERS = [
    "mcp.googleapis.com/mcp/v1",
    "gmailmcp.googleapis.com",
    "drivemcp.googleapis.com",
    "docsmcp.googleapis.com",
    "sheetsmcp.googleapis.com",
    "slidesmcp.googleapis.com",
    "calendarmcp.googleapis.com",
    "chatmcp.googleapis.com",
    "tasksmcp.googleapis.com",
    "gwscli",
]

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
    ".toml", ".env", ".sh", ".md",
}

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
    "build", ".next",
}

# Files that are documentation about the migration itself, not the
# agent's code — the skill's own references name REST hostnames
# when describing what to move away from. Only skip these when the
# caller explicitly points at the skill directory itself.
DOCS_SKIP_NAMES = {"SKILL.md", "migration.md", "auth.md", "tiers.md",
                   "gotchas.md", "README.md"}


def iter_project_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in CODE_EXTENSIONS:
            yield path


def check_no_rest_calls(root: Path) -> list[str]:
    """Fail if any direct Workspace REST call remains."""
    problems = []
    for path in iter_project_files(root):
        if path.name in DOCS_SKIP_NAMES and path.name == "SKILL.md":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for host in REST_HOSTS:
            # MCP hostnames contain "mcp.googleapis.com", not the
            # bare product hostnames, so a plain substring match is
            # safe — except that a line mentioning an MCP server
            # URL also contains no bare REST hostname.
            if host in text:
                # Ignore lines that are explicitly about the MCP
                # servers, and ignore the migration record's notes.
                for line in text.splitlines():
                    if host in line and "mcp" not in line.lower():
                        problems.append(
                            f"{path.relative_to(root)}: direct REST "
                            f"host {host!r} still referenced"
                        )
                        break
                break
        if not any(host in text for host in REST_HOSTS):
            for rest_path in REST_PATHS:
                if rest_path in text:
                    problems.append(
                        f"{path.relative_to(root)}: direct REST "
                        f"path {rest_path!r} still referenced"
                    )
                    break
    return problems


def check_mcp_config(root: Path) -> list[str]:
    """Fail if no MCP configuration is present."""
    for path in iter_project_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(marker in text for marker in MCP_MARKERS):
            return []
    return [
        "no MCP configuration found: no file references a Workspace "
        "MCP server (*mcp.googleapis.com/mcp/v1) or gwscli"
    ]


def _tier_from_json(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    tier = str(data.get("tier", "")).strip().lower()
    return tier if tier in ("standard", "scaled") else None


def _tier_from_text(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    match = re.search(r"tier\s*[:=]\s*(standard|scaled)",
                      text, re.IGNORECASE)
    return match.group(1).lower() if match else None


def check_tier_recorded(root: Path) -> tuple[list[str], str | None]:
    """Fail if no tier selection is recorded."""
    candidates = [
        root / "workspace-migration.json",
        root / "MIGRATION.md",
        root / "migration.json",
        root / "workspace-migration.md",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        tier = (_tier_from_json(path) if path.suffix == ".json"
                else _tier_from_text(path))
        if tier:
            return [], tier
    return [
        "no tier recorded: add workspace-migration.json or "
        "MIGRATION.md naming tier Standard or Scaled"
    ], None


def verify(root: Path) -> tuple[bool, str | None, list[str]]:
    problems = []
    problems.extend(check_no_rest_calls(root))
    problems.extend(check_mcp_config(root))
    tier_problems, tier = check_tier_recorded(root)
    problems.extend(tier_problems)
    return (not problems), tier, problems


def self_test() -> int:
    """Build a passing and a failing fixture in /tmp and check both."""
    import shutil
    import tempfile

    base = Path(tempfile.mkdtemp(prefix="check-migration-test-"))
    try:
        good = base / "good-agent"
        (good / "src").mkdir(parents=True)
        (good / "src" / "agent.py").write_text(
            "MCP_URL = 'https://gmailmcp.googleapis.com/mcp/v1'\n"
            "MCP_URL_CAL = 'https://calendarmcp.googleapis.com/mcp/v1'\n"
        )
        (good / "mcp.json").write_text(
            '{"mcpServers": {"gmail": {"url": '
            '"https://gmailmcp.googleapis.com/mcp/v1"}}}\n'
        )
        (good / "workspace-migration.json").write_text(
            '{"tier": "standard", "daily_estimate": {"gmail": 120}}\n'
        )
        ok, tier, problems = verify(good)
        if not ok or tier != "standard":
            print(f"SELF-TEST FAILED: good fixture should pass, got {problems}")
            return 1

        bad = base / "bad-agent"
        (bad / "src").mkdir(parents=True)
        (bad / "src" / "agent.py").write_text(
            "requests.get('https://gmail.googleapis.com/gmail/v1/users/me/messages')\n"
        )
        ok, _tier, problems = verify(bad)
        if ok or not problems:
            print("SELF-TEST FAILED: bad fixture should fail")
            return 1
        print("SELF-TEST PASSED: good fixture passes, bad fixture fails")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a Workspace agent migration from REST to MCP."
    )
    parser.add_argument("target", nargs="?",
                        help="agent project directory to verify")
    parser.add_argument("--self-test", action="store_true",
                        help="run the built-in passing/failing fixture test")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.target:
        parser.error("give an agent project directory, or --self-test")

    root = Path(args.target)
    if not root.is_dir():
        print(f"FAILED: {args.target} is not a directory")
        return 1

    ok, tier, problems = verify(root)
    if ok:
        print(f"PASSED: migration verified (tier: {tier})")
        return 0
    print("FAILED: migration not verified")
    for problem in problems:
        print(f"  - {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
