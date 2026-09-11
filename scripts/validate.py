#!/usr/bin/env python3
"""Offline package and local-link checks using Python's standard library."""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from check_upstream import load_lock

ROOT = Path(__file__).resolve().parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def anchors(text):
    counts = {}
    found = set()
    fenced = False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        if fenced or not re.match(r"^#{1,6} ", line):
            continue
        title = re.sub(r"^#+ ", "", line).strip().lower()
        title = re.sub(r"[^\w\- ]", "", title, flags=re.UNICODE).replace(" ", "-")
        count = counts.get(title, 0)
        counts[title] = count + 1
        found.add(f"{title}-{count}" if count else title)
    return found


def validate():
    required = ["SKILL.md", "README.md", "README.en.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "CHANGELOG.md", "agents/openai.yaml", "evals/cases.json", "assets/banner.svg"]
    for path in required:
        require((ROOT / path).is_file(), f"Missing {path}")
    skill = read("SKILL.md")
    front = re.match(r"\A---\n(.*?)\n---\n", skill, re.S)
    require(front, "SKILL.md needs YAML frontmatter")
    header = front.group(1)
    keys = re.findall(r"^([\w-]+):", header, re.M)
    require(sorted(keys) == ["description", "license", "metadata", "name"], "Keep only the expected skill metadata fields")
    require(re.search(r"^name: humanizer-zh$", header, re.M), "Skill name must be humanizer-zh")
    version_match = re.search(r'^  version: "(\d+\.\d+\.\d+)"$', header, re.M)
    require(version_match, "Use quoted metadata.version with three parts")
    version = version_match.group(1)
    require(not (ROOT / "SKILL.md").is_symlink(), "The root skill must be a regular file")
    copies = [path for path in ROOT.rglob("SKILL.md") if not any(part in {".git", "node_modules", ".venv"} for part in path.relative_to(ROOT).parts)]
    require(copies == [ROOT / "SKILL.md"], "Keep exactly one root SKILL.md")
    require(len(skill.splitlines()) <= 250 and len(skill.encode()) <= 24000, "Keep the self-contained skill under 250 lines and 24 KB; review any growth")

    plugin = json.loads(read(".claude-plugin/plugin.json"))
    market = json.loads(read(".claude-plugin/marketplace.json"))
    require(plugin["name"] == market["name"] == "humanizer-zh", "Plugin and marketplace names must match the installation commands")
    require(plugin["version"] == version, "Skill and plugin versions differ")
    require(plugin["skills"] == ["./"], "Claude must load the single root skill")
    require(not any(key in plugin for key in ["hooks", "mcpServers", "commands"]), "This package should remain instruction-only")
    require(len(market["plugins"]) == 1, "The marketplace should contain one plugin")
    entry = market["plugins"][0]
    require(entry["name"] == plugin["name"] and entry["source"] == "./", "Marketplace must resolve the root plugin")
    require("version" not in entry, "Keep the plugin version in plugin.json only")
    for path in ["README.md", "README.en.md"]:
        require(f"**{version}**" in read(path), f"Update current version in {path}")
        require("npx skills add tonyyunyang/humanizer-zh --global" in read(path), f"Missing canonical installation command in {path}")
    require(re.search(rf"^## {re.escape(version)} [—-] ", read("CHANGELOG.md"), re.M), "Add this version to the changelog")

    lock = load_lock(ROOT / "upstream.lock.json")
    for source in lock["sources"]:
        require(source["revision"] in read("docs/UPSTREAM.md"), f"Document the reviewed commit for {source['id']}")
    upstream_version = next(source["version"] for source in lock["sources"] if source["id"] == "blader")
    # Upstream provenance belongs to maintenance records, not the runtime skill.
    require(f"Blader Humanizer {upstream_version}" in read("README.md"), "README's upstream version differs from the lock")
    require("Copyright (c) 2026 Tony Yang" in read("LICENSE"), "Preserve the existing repository license")
    for owner in ["2025 Siqi Chen", "2026 MrGeDiao", "2026 歸藏"]:
        require(f"Copyright (c) {owner}" in read("THIRD_PARTY_NOTICES.md"), f"Missing upstream notice for {owner}")
    ET.parse(ROOT / "assets/banner.svg")

    cases = json.loads(read("evals/cases.json"))
    require(cases and len({case["id"] for case in cases}) == len(cases), "Regression case IDs must be unique")
    for case in cases:
        require(all(case.get(key) for key in ["id", "request", "input", "expectations"]), f"Incomplete regression case: {case.get('id')}")

    # Check repository links. External services are deliberately not required for offline checks.
    for path in ROOT.rglob("*.md"):
        if any(part in {".git", "node_modules", ".venv"} for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            link = urllib.parse.urlsplit(target)
            if link.scheme or link.netloc:
                continue
            dest = (path.parent / urllib.parse.unquote(link.path)).resolve() if link.path else path
            require(dest.is_relative_to(ROOT), f"Link escapes the repo in {path.relative_to(ROOT)}: {target}")
            require(dest.exists(), f"Broken link in {path.relative_to(ROOT)}: {target}")
            if link.fragment and dest.suffix == ".md":
                require(urllib.parse.unquote(link.fragment) in anchors(dest.read_text(encoding="utf-8")), f"Missing heading in {path.relative_to(ROOT)}: {target}")
    print(f"Package v{version} is valid: one skill, matching manifests, source records, notices and local links.")
    print("This is a structural check, not a model behavior evaluation.")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ValueError, KeyError, StopIteration, ET.ParseError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
