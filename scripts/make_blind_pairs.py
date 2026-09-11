#!/usr/bin/env python3
"""Prepare anonymous output comparisons without exposing revision identities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random

from run_evals import sha256, write_json

RUBRIC = """你是中文编辑评审。根据原文、用户要求、样文和验收要点，比较匿名改稿 A、B。
先逐项检查实质信息：事实、数字、角色和归属、否定、条件、范围、时序、完成状态、作者立场和语气、引文与精确字符。
作者有意表达的评价、偏好、预测和修辞也需要保护。普通的等义改写不算错误；不能仅因某词像套话就判错，也不要因某版更短而偏爱它。
只有完成任务且保住这些内容后，才比较承接、用词、节奏和文体。允许原文不改，允许长句、排比、修辞和中英混排。改变内容或明显违反请求的为 fail；有实质歧义而无法确定的为 uncertain；否则为 pass。
每条问题都需给出原文依据、改稿片段和具体差异，不推测作者没说的动机。纯审美偏好不要记成硬错误。
两版各有取舍、无明确收益时可以平局；材料不足时选择 uncertain。只按给定 JSON schema 输出，不猜版本身份。"""


def load_run(directory):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "complete" or manifest["repeats"] != 1:
        raise ValueError("Compare complete single-repetition runs; keep invalid or repeated runs separate")
    outputs = {}
    for name in manifest["case_ids"]:
        result = json.loads((directory / f"{name}-1.json").read_text(encoding="utf-8"))
        if result["status"] != "ok" or not result.get("output"):
            raise ValueError(f"Invalid output: {name}")
        outputs[name] = result["output"]
    return manifest, outputs


def prepare(suite, manifest_a, outputs_a, manifest_b, outputs_b, seed):
    for field in ("model", "effort", "suite_sha256", "case_ids", "partition"):
        if manifest_a[field] != manifest_b[field]:
            raise ValueError(f"Unmatched comparison setting: {field}")
    index = {case["id"]: case for case in suite}
    rng = random.Random(seed)
    tasks, mapping = [], {}
    for name in manifest_a["case_ids"]:
        original = index[name]
        flipped = bool(rng.getrandbits(1))
        a, b = (outputs_b[name], outputs_a[name]) if flipped else (outputs_a[name], outputs_b[name])
        material = {key: original[key] for key in ("request", "sample", "input", "expectations") if key in original}
        material.update({"A": a, "B": b})
        tasks.append({"id": name, "request": RUBRIC,
                      "input": json.dumps(material, ensure_ascii=False, indent=2)})
        mapping[name] = {"A": "second" if flipped else "first", "B": "first" if flipped else "second"}
    return tasks, mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--first", type=Path, required=True)
    parser.add_argument("--second", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    suite_text = args.suite.read_text(encoding="utf-8")
    first, outputs_first = load_run(args.first)
    second, outputs_second = load_run(args.second)
    if sha256(suite_text) != first["suite_sha256"]:
        raise ValueError("Suite changed after generation")
    tasks, mapping = prepare(json.loads(suite_text), first, outputs_first, second, outputs_second, args.seed)
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "tasks.json", tasks)
    write_json(args.output / "mapping.json", {
        "first": {"run": str(args.first), "skill_commit": first["skill_commit"]},
        "second": {"run": str(args.second), "skill_commit": second["skill_commit"]},
        "seed": args.seed, "cases": mapping,
        "note": "Keep this mapping out of all judge prompts; first/second identities are not in tasks.json.",
    })
    print(f"Prepared {len(tasks)} anonymous comparisons")


if __name__ == "__main__":
    main()
