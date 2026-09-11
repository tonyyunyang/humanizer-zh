#!/usr/bin/env python3
"""Test the real Skills CLI in a disposable project; never install globally."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_VERSION = "1.5.25"


def main():
    env = dict(os.environ, CI="1", DISABLE_TELEMETRY="1", DO_NOT_TRACK="1")
    npx = "npx.cmd" if os.name == "nt" else "npx"
    base = [npx, "--yes", f"skills@{SKILLS_VERSION}", "add", str(ROOT)]
    with tempfile.TemporaryDirectory(prefix="humanizer-zh-install-") as directory:
        for args in [["--list"], ["--skill", "humanizer-zh", "--agent", "claude-code", "codex", "--yes"]]:
            subprocess.run(base + args, cwd=directory, env=env, check=True, timeout=180)
        for agent in [".agents", ".claude"]:
            installed = Path(directory) / agent / "skills" / "humanizer-zh"
            for filename in ["SKILL.md", "LICENSE", "THIRD_PARTY_NOTICES.md"]:
                if (installed / filename).read_bytes() != (ROOT / filename).read_bytes():
                    raise RuntimeError(f"The installed {agent}/{filename} differs from the source")
    print(f"Skills CLI {SKILLS_VERSION}: discovery and Claude Code/Codex project installation passed.")


if __name__ == "__main__":
    main()
