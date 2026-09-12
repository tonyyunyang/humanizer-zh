#!/usr/bin/env python3
"""Build an explicitly derived view after retrying failed executions only."""

import argparse
import json
from pathlib import Path
import re
import shutil

from run_evals import write_json

SETTINGS = (
    "skill_commit", "skill_sha256", "suite_sha256", "model", "effort",
    "cli_version", "runner_sha256", "schema_sha256", "timeout_seconds", "partition", "repeats",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def select_results(base, retries):
    manifest = read_json(base / "manifest.json")
    if manifest["status"] not in {"complete", "incomplete"} or manifest["repeats"] != 1:
        raise ValueError("Use finished, single-repetition batches")
    selected, failed_attempts = {}, []
    for name in manifest["case_ids"]:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            raise ValueError("Invalid case ID")
        path = base / f"{name}-1.json"
        selected[name] = path
        if read_json(path)["status"] != "ok":
            failed_attempts.append(str(path))
    attempt_count = manifest["total_runs"]
    for retry in retries:
        retried = read_json(retry / "manifest.json")
        if retried["status"] not in {"complete", "incomplete"}:
            raise ValueError("Retry batch still running")
        if any(manifest[key] != retried[key] for key in SETTINGS):
            raise ValueError("Retry changed generation or judging settings")
        attempt_count += retried["total_runs"]
        for name in retried["case_ids"]:
            if name not in selected:
                raise ValueError("Retry includes a new case")
            old = read_json(selected[name])
            new_path = retry / f"{name}-1.json"
            new = read_json(new_path)
            if old["status"] == "ok":
                raise ValueError("Cannot replace a successful execution, even if its quality was poor")
            if not old.get("prompt_sha256") or old["prompt_sha256"] != new.get("prompt_sha256"):
                raise ValueError("Retry prompt differs or cannot be verified")
            selected[name] = new_path
            if new["status"] != "ok":
                failed_attempts.append(str(new_path))
    if any(read_json(path)["status"] != "ok" for path in selected.values()):
        raise ValueError("Some executions remain invalid; original records are unchanged")
    return manifest, selected, failed_attempts, attempt_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--retry", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest, selected, failed, attempts = select_results(args.base, args.retry)
    args.output.mkdir(parents=True, exist_ok=False)
    for name, path in selected.items():
        shutil.copyfile(path, args.output / f"{name}-1.json")
    manifest.update({
        "status": "complete", "valid_runs": len(selected), "total_runs": len(selected),
        "derived_snapshot": True, "attempt_count": attempts,
        "source_batches": [str(args.base)] + [str(path) for path in args.retry],
        "selected_from": {name: str(path) for name, path in selected.items()},
        "failed_attempts": failed,
        "note": "Derived view, not another model run. Original failures remain in their source batches; only invalid executions can be replaced.",
    })
    write_json(args.output / "manifest.json", manifest)
    print(f"Selected {len(selected)} valid outputs from {attempts} attempts; retained {len(failed)} failed records")


if __name__ == "__main__":
    main()
