#!/usr/bin/env python3
"""Compare reviewed Git blobs with upstream. Writes only with explicit flags."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
MARKER = "<!-- humanizer-zh:upstream-review:v1 -->"
BOT = "github-actions[bot]"
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA = re.compile(r"[0-9a-f]{40}")


class GitHub:
    def __init__(self, token: str | None = None):
        self.token = token

    def request(self, method: str, path: str, data=None):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "humanizer-zh-upstream"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        body = None
        if data is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data, ensure_ascii=False).encode()
        request = urllib.request.Request("https://api.github.com" + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            # Do not print headers, token, or response bodies.
            raise RuntimeError(f"GitHub HTTP {error.code} for {method} {path}") from None
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            raise RuntimeError(f"GitHub request failed for {method} {path}: {type(error).__name__}") from None


def load_lock(path: Path) -> dict:
    lock = json.loads(path.read_text(encoding="utf-8"))
    if lock.get("schema_version") != 1 or not lock.get("sources"):
        raise ValueError("Expected schema_version 1 and nonempty sources")
    ids = set()
    for source in lock["sources"]:
        source_id = source.get("id", "")
        if not re.fullmatch(r"[a-z0-9-]+", source_id) or source_id in ids:
            raise ValueError("Source IDs must be unique lowercase names")
        ids.add(source_id)
        if not REPOSITORY.fullmatch(source.get("repository", "")):
            raise ValueError(f"Invalid repository for {source_id}")
        if not SHA.fullmatch(source.get("revision", "")):
            raise ValueError(f"Expected a full reviewed SHA for {source_id}")
        dt.date.fromisoformat(source["reviewed_on"])
        if not isinstance(source.get("branch"), str) or not source["branch"]:
            raise ValueError(f"Expected a branch for {source_id}")
        if not isinstance(source.get("files"), dict) or not source["files"]:
            raise ValueError(f"Expected tracked files for {source_id}")
        for filename, blob in source["files"].items():
            path_parts = PurePosixPath(filename)
            if path_parts.is_absolute() or ".." in path_parts.parts or not filename or "\\" in filename:
                raise ValueError(f"Unsafe tracked path: {filename}")
            if not SHA.fullmatch(blob):
                raise ValueError(f"Expected a blob SHA for {filename}")
    return lock


def snapshot(api: GitHub, source: dict, ref: str) -> tuple[str, dict[str, str]]:
    repository = source["repository"]
    commit = api.request("GET", f"/repos/{repository}/commits/{urllib.parse.quote(ref, safe='')}")
    revision = commit["sha"]
    tree_sha = commit["commit"]["tree"]["sha"]
    if not SHA.fullmatch(revision) or not SHA.fullmatch(tree_sha):
        raise ValueError("GitHub returned an invalid commit or tree SHA")
    tree = api.request("GET", f"/repos/{repository}/git/trees/{tree_sha}?recursive=1")
    if tree.get("truncated"):
        raise ValueError(f"Tree is truncated for {repository}; cannot conclude files are unchanged")
    if not isinstance(tree.get("tree"), list):
        raise ValueError(f"Missing tree for {repository}")
    blobs = {item["path"]: item["sha"] for item in tree["tree"] if item["type"] == "blob"}
    return revision, blobs


def inspect_sources(api: GitHub, lock: dict) -> list[dict]:
    changes = []
    for source in lock["sources"]:
        head, blobs = snapshot(api, source, source["branch"])
        paths = [path for path, previous in source["files"].items() if blobs.get(path) != previous]
        if paths:
            changes.append({"repository": source["repository"], "reviewed": source["revision"], "head": head, "paths": paths})
    return changes


def render_report(changes: list[dict]) -> str:
    lines = [MARKER, "# 上游参考有新变化", "", "以下文件与已审阅记录不同。请先判断中文适用性，再更新 skill 和审阅基线。", ""]
    for change in changes:
        base = f"https://github.com/{change['repository']}"
        lines.extend([
            f"## {change['repository']}", "",
            f"- 已审阅：[`{change['reviewed'][:7]}`]({base}/tree/{change['reviewed']})",
            f"- 当前提交：[`{change['head'][:7]}`]({base}/tree/{change['head']})",
            f"- [查看差异]({base}/compare/{change['reviewed']}...{change['head']})",
            "- 变化或删除的跟踪文件：" + "、".join(f"`{path}`" for path in change["paths"]), "",
        ])
    lines.extend([
        "审阅流程见 [docs/UPSTREAM.md](https://github.com/tonyyunyang/humanizer-zh/blob/main/docs/UPSTREAM.md)。",
        "采用、改写或跳过都需要留下理由；补中文例子并检查后，再更新 `upstream.lock.json`。",
        "", "机器人维护此 Issue 正文，人工审阅意见请写在评论或 PR 中。仅关闭 Issue 不会推进基线；未审阅的差异仍在时会重新打开。",
    ])
    return "\n".join(lines) + "\n"


def find_review_issue(api: GitHub, repository: str):
    page = 1
    while True:
        items = api.request("GET", f"/repos/{repository}/issues?state=all&per_page=100&page={page}")
        for item in items:
            if "pull_request" not in item and item.get("user", {}).get("login") == BOT and MARKER in (item.get("body") or ""):
                return item
        if len(items) < 100:
            return None
        page += 1


def sync_issue(api: GitHub, repository: str, changes: list[dict]) -> str:
    if not REPOSITORY.fullmatch(repository):
        raise ValueError("Expected owner/repository for the issue destination")
    issue = find_review_issue(api, repository)
    endpoint = f"/repos/{repository}/issues"
    if not changes:
        if issue and issue["state"] == "open":
            api.request("PATCH", f"{endpoint}/{issue['number']}", {"state": "closed"})
            return "Closed the resolved review issue."
        return "No tracked content changed; no issue written."
    body = render_report(changes)
    if issue is None:
        api.request("POST", endpoint, {"title": "[上游同步] 参考项目有变更待审阅", "body": body})
        return "Created one upstream review issue."
    update = {}
    if issue["body"] != body:
        update["body"] = body
    if issue["state"] != "open":
        update["state"] = "open"
    if update:
        api.request("PATCH", f"{endpoint}/{issue['number']}", update)
        return "Updated the upstream review issue."
    return "The review issue already contains these changes; no write needed."


def record_review(api: GitHub, path: Path, lock: dict, source_id: str, ref: str):
    if not SHA.fullmatch(ref):
        raise ValueError("--ref must be the full 40-character commit SHA you reviewed")
    source = next((source for source in lock["sources"] if source["id"] == source_id), None)
    if source is None:
        raise ValueError(f"Unknown source ID: {source_id}")
    revision, blobs = snapshot(api, source, ref)
    if revision != ref:
        raise ValueError("Resolved commit does not match the reviewed SHA")
    missing = set(source["files"]) - blobs.keys()
    if missing:
        raise ValueError(f"Review removed/renamed paths before recording: {sorted(missing)}")
    source["files"] = {filename: blobs[filename] for filename in source["files"]}
    source["revision"] = revision
    source["reviewed_on"] = dt.datetime.now(dt.timezone.utc).date().isoformat()
    path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=ROOT / "upstream.lock.json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--issue", action="store_true", help="Maintain a bot-owned issue in GitHub Actions")
    mode.add_argument("--record", metavar="SOURCE_ID", help="Record a commit after editorial review")
    parser.add_argument("--ref", help="Full reviewed SHA; only valid with --record")
    args = parser.parse_args()
    if bool(args.record) != bool(args.ref):
        parser.error("Use --record and --ref together")
    if args.issue and (os.environ.get("GITHUB_ACTIONS") != "true" or not os.environ.get("GITHUB_TOKEN")):
        parser.error("--issue requires GitHub Actions and its GITHUB_TOKEN")
    try:
        lock = load_lock(args.lock)
        api = GitHub(os.environ.get("GITHUB_TOKEN"))
        if args.record:
            record_review(api, args.lock, lock, args.record, args.ref)
            print("Recorded the reviewed commit. Also review version metadata and the written adaptation record.")
        else:
            # Read every source successfully before creating, editing, or closing an issue.
            changes = inspect_sources(api, lock)
            if args.issue:
                print(sync_issue(api, os.environ.get("GITHUB_REPOSITORY", ""), changes))
            else:
                print(render_report(changes) if changes else "No tracked upstream content changed.")
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        print(f"Upstream check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
