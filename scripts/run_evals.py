#!/usr/bin/env python3
"""Run isolated, text-only Codex editing cases and retain ungraded evidence."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
DISABLED_FEATURES = (
    "apps", "plugins", "memories", "multi_agent", "hooks", "skill_search",
    "shell_tool", "browser_use", "computer_use",
)
ALLOWED_ITEM_TYPES = {"agent_message", "reasoning", "error"}


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def chatgpt_environment():
    env = os.environ.copy()
    for name in ("CODEX_API_KEY", "OPENAI_API_KEY"):
        env.pop(name, None)
    return env


def require_chatgpt_login():
    result = subprocess.run(["codex", "login", "status"], capture_output=True, text=True,
                            env=chatgpt_environment(), timeout=15)
    if result.returncode or "logged in using chatgpt" not in (result.stdout + result.stderr).lower():
        raise ValueError("This runner requires a saved ChatGPT login; it does not use API-key auth")


def select_cases(path, ids, exclude, partition):
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("Suite must be a nonempty list")
    seen = set()
    for case in cases:
        name = case.get("id", "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) or name in seen:
            raise ValueError(f"Invalid or duplicate case id: {name}")
        if not all(isinstance(case.get(key), str) and case[key] for key in ("request", "input")):
            raise ValueError(f"Missing request or input: {name}")
        if "sample" in case and not isinstance(case["sample"], str):
            raise ValueError(f"Sample must be text: {name}")
        seen.add(name)
    unknown = (set(ids) | set(exclude)) - seen
    if unknown:
        raise ValueError(f"Unknown case ids: {sorted(unknown)}")
    selected = [c for c in cases if (not ids or c["id"] in ids)
                and c["id"] not in exclude
                and (not partition or c.get("partition") == partition)]
    if not selected:
        raise ValueError("No cases selected")
    return selected


def make_prompt(case, skill):
    public = {key: case[key] for key in ("request", "sample", "input") if key in case}
    prompt = "请完成下面的用户任务，仅输出任务所需的内容。全部材料已在提示中，无需使用工具。\n\n"
    if skill is not None:
        prompt += "请采用以下编辑规范。\n<editing_guidance>\n" + skill + "\n</editing_guidance>\n\n"
    return prompt + "<user_task>\n" + json.dumps(public, ensure_ascii=False, indent=2) + "\n</user_task>\n"


def command(model, effort, workspace, schema=None):
    args = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
            "--sandbox", "read-only", "--json", "--color", "never", "-m", model,
            "-c", f'model_reasoning_effort="{effort}"', "-c", 'approval_policy="never"',
            "-c", "project_doc_max_bytes=0", "-c", 'web_search="disabled"',
            "-c", "suppress_unstable_features_warning=true", "--enable", "skip_host_skill_discovery"]
    for feature in DISABLED_FEATURES:
        args.extend(["--disable", feature])
    if schema:
        args.extend(["--output-schema", str(schema)])
    return args + ["-C", str(workspace), "-o", str(workspace / "output.txt"), "-"]


def parse_events(stdout):
    usage, errors, warnings, tools_used = None, [], [], []
    completed = False
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            errors.append("Non-JSON stdout event")
            continue
        kind = event.get("type")
        if kind == "turn.completed":
            completed, usage = True, event.get("usage")
        elif kind in {"turn.failed", "error"}:
            errors.append(event.get("error", event.get("message", kind)))
        elif kind and kind.startswith("item."):
            item = event.get("item", {})
            item_type = item.get("type")
            if item_type == "error":
                warnings.append(item.get("message", "Item error"))
            elif item_type and item_type not in ALLOWED_ITEM_TYPES:
                tools_used.append(item_type)
    return {"completed": completed, "usage": usage, "errors": errors,
            "warnings": warnings, "tools_used": sorted(set(tools_used))}


def run_case(case, skill, args, repetition):
    prompt = make_prompt(case, skill)
    started = time.monotonic()
    timed_out = False
    # Reuse saved ChatGPT sign-in; do not accidentally switch to an inherited API key.
    env = chatgpt_environment()
    with tempfile.TemporaryDirectory(prefix="humanizer-eval-") as directory:
        workspace = Path(directory)
        process = subprocess.Popen(command(args.model, args.effort, workspace, args.schema),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, env=env, start_new_session=True, cwd=workspace)
        try:
            stdout, stderr = process.communicate(prompt, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
        evidence = parse_events(stdout)
        output_path = workspace / "output.txt"
        output = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    ok = (not timed_out and process.returncode == 0 and evidence["completed"]
          and not evidence["errors"] and not evidence["warnings"]
          and not evidence["tools_used"] and bool(output))
    if args.schema and output:
        try:
            json.loads(output)
        except json.JSONDecodeError:
            ok = False
            evidence["errors"].append("Structured output was not JSON")
    return {"case_id": case["id"], "repetition": repetition, "status": "ok" if ok else "invalid",
            "exit_code": process.returncode, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "prompt_sha256": sha256(prompt), "output": output, **evidence,
            "stderr_sha256": sha256(stderr), "stderr_lines": len(stderr.splitlines())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=ROOT / "evals/cases.json")
    parser.add_argument("--skill-ref", default="HEAD", help="Committed skill revision; use none for judging")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), required=True)
    parser.add_argument("--ids", nargs="*", default=[])
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("--partition", choices=("development", "holdout"))
    parser.add_argument("--jobs", type=int, default=2, choices=range(1, 5))
    parser.add_argument("--repeats", type=int, default=1, choices=range(1, 4))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--schema", type=Path)
    args = parser.parse_args()
    if not 10 <= args.timeout <= 600:
        parser.error("Timeout must be 10–600 seconds")
    args.suite = args.suite.resolve()
    args.schema = args.schema.resolve() if args.schema else None
    cases = select_cases(args.suite, args.ids, args.exclude, args.partition)
    require_chatgpt_login()
    skill_ref = None
    skill = None
    if args.skill_ref != "none":
        skill_ref = subprocess.check_output(["git", "rev-parse", "--verify", args.skill_ref + "^{commit}"], cwd=ROOT, text=True).strip()
        skill = subprocess.check_output(["git", "show", skill_ref + ":SKILL.md"], cwd=ROOT, text=True)
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {"started_at": datetime.now(timezone.utc).isoformat(), "status": "running",
                "skill_commit": skill_ref, "skill_sha256": sha256(skill) if skill else None,
                "suite_sha256": sha256(args.suite.read_text(encoding="utf-8")),
                "case_ids": [c["id"] for c in cases], "excluded_ids": args.exclude,
                "partition": args.partition, "repeats": args.repeats, "jobs": args.jobs,
                "timeout_seconds": args.timeout, "model": args.model, "effort": args.effort,
                "cli_version": subprocess.check_output(["codex", "--version"], text=True).strip(),
                "runner_sha256": sha256(Path(__file__).read_text(encoding="utf-8")),
                "schema_sha256": sha256(args.schema.read_text(encoding="utf-8")) if args.schema else None,
                "context": "Fresh text-only sessions; no expected answers in editing prompts; host skill discovery skipped; user config, project docs, memory, apps, plugins and tools disabled where supported.",
                "limitations": ["Same underlying model family may share editing and judging biases.",
                                "Codex base instructions remain; this is not a bare-model API test.",
                                "Host skill discovery suppression uses an under-development CLI feature.",
                                "File-editing behavior is outside this text-only runner."]}
    write_json(args.output / "manifest.json", manifest)
    results = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_case, c, skill, args, repetition): (c["id"], repetition)
                   for c in cases for repetition in range(1, args.repeats + 1)}
        for future in as_completed(futures):
            name, repetition = futures[future]
            try:
                result = future.result()
            except Exception as error:
                result = {"case_id": name, "repetition": repetition, "status": "invalid",
                          "errors": [f"{type(error).__name__}: {error}"]}
            results.append(result)
            write_json(args.output / f"{name}-{repetition}.json", result)
            print(f"{name} #{repetition}: {result['status']}", flush=True)
    manifest.update({"status": "complete" if all(r["status"] == "ok" for r in results) else "incomplete",
                     "finished_at": datetime.now(timezone.utc).isoformat(),
                     "valid_runs": sum(r["status"] == "ok" for r in results), "total_runs": len(results)})
    write_json(args.output / "manifest.json", manifest)
    return 0 if manifest["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
