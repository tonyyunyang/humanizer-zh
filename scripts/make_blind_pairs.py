#!/usr/bin/env python3
"""Prepare anonymous output comparisons without exposing revision identities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random

from run_evals import sha256, write_json

RUBRIC = """你是中文编辑评审。根据原文、用户要求、上下文、可选样文和验收要点，比较匿名改稿 A、B。
先用一句话说明这一次具体想完成的表达：读者需要理解、感受或据此做什么。不要用文体名称代替这个判断，也不要擅自给原文增加情绪或立场。
检查事实、数字、角色与归属、否定、条件、范围、时序、完成状态、作者实质立场、引文和精确字符，以及用户明确的修改边界。语气和表达方式可以按用户意图调整，等义改写不算错误。有实质信息错误或明确范围违背的为 fail；影响结论而不能确定的为 uncertain；否则为 pass。纯审美取舍不记成硬错误。
在信息与范围成立后，按这一次的目的比较：重点、解释程度和力度是否贴切；措辞、语序、承接、省略和停顿是否自然；有没有残留或新加的模板式铺垫、抽象空转、机械排比、强行收尾或无依据的姿态。
template_issues 只记录改稿中能定位且在此处没有作用的模板问题，引用原文和改稿说明原因；不能因为一个词、一个转折、三项列举或一处修辞就贴标签。没有这类问题时用空数组，不推测作者是否是 AI。
平直可以很好，不默认奖励更短、口语化、更明确或更多修辞。需要表现力时，检查改稿是否通过已有意思的措辞、句序、节奏或呼应达到效果；不能仅因保留原文就算完成改进。原文已经适合本次需要时，少改或不改也可成立。不要把有作用的含蓄补成解释，也不要为平直文字硬添意味。
reason 要把偏好联系到具体表达目的、自然中文和去模板效果，并引用相关差异。两版各有取舍或收益不清时允许 tie；材料不足时选 uncertain。只按给定 JSON schema 输出，不猜版本身份。"""


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
    for field in ("model", "effort", "suite_sha256", "case_ids", "partition",
                  "cli_version", "runner_sha256", "timeout_seconds", "schema_sha256"):
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
        "rubric_sha256": sha256(RUBRIC),
        "note": "Keep this mapping out of all judge prompts; first/second identities are not in tasks.json.",
    })
    print(f"Prepared {len(tasks)} anonymous comparisons")


if __name__ == "__main__":
    main()
