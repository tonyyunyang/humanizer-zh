#!/usr/bin/env python3
"""Prepare single-output audits before deciding whether a skill needs a candidate."""

import argparse
import json
from pathlib import Path

from make_blind_pairs import load_run
from run_evals import sha256, write_json

RUBRIC = """你是中文编辑评审。根据用户要求、原始材料、可选样文和验收要点，审查给出的一份成稿。
先说明本次具体要完成的表达，再核对实质信息、条件、范围、时序、作者立场、精确字符与明确修改边界。遗漏或改变实质信息、违反明确范围、增加无法由材料支持的确定事实，都使 information_gate 为 fail；即使无法知道新增断言在现实中是否为真，也不能只记为 uncertain。只有材料或表达本身有歧义，无法确定是否发生上述错误时才用 uncertain；否则为 pass。每个问题都引用输入与成稿中的具体证据，等义改写不算错误。
以本次材料为依据，不要求每项作者陈述都另外附证明，也不把未提供的材料补成结论。材料之间有冲突时，依据任务指定的范围和各材料的用途判断，不能确定就说明不确定。
再判断成稿是否完成了这次表达：重点、组织、解释程度和语气是否合适，读者能否完成请求所需的理解、感受或判断。task_fit 使用 adequate、needs_work 或 uncertain；不因个人更喜欢另一种措辞就判 needs_work。
template_issues 只记录成稿中可定位、在此处没有作用的模板表达。允许平直、充分说明、作者有意的重复与含蓄；不按长度、标题数量或是否有修辞评好坏。没有问题时数组为空，不为审查而硬找缺点。只按给定 JSON schema 输出。"""


def prepare(suite_text, manifest, outputs):
    if sha256(suite_text) != manifest["suite_sha256"]:
        raise ValueError("Suite changed after generation")
    index = {case["id"]: case for case in json.loads(suite_text)}
    tasks = []
    for name in manifest["case_ids"]:
        if name not in index or name not in outputs:
            raise ValueError(f"Missing source or output for {name}")
        case = index[name]
        material = {key: case[key] for key in ("request", "sample", "input", "expectations") if key in case}
        material["output"] = outputs[name]
        tasks.append({"id": name, "request": RUBRIC,
                      "input": json.dumps(material, ensure_ascii=False, indent=2)})
    return tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest, outputs = load_run(args.run)
    tasks = prepare(args.suite.read_text(encoding="utf-8"), manifest, outputs)
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "tasks.json", tasks)
    write_json(args.output / "source.json", {
        "source_run": str(args.run), "skill_commit": manifest["skill_commit"],
        "suite_sha256": manifest["suite_sha256"], "rubric_sha256": sha256(RUBRIC),
        "note": "Single-output audit, not a version comparison. Source metadata is excluded from judge prompts.",
    })
    print(f"Prepared {len(tasks)} single-output audits")


if __name__ == "__main__":
    main()
