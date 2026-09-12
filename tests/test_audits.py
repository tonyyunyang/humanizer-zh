import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from make_audit_tasks import prepare
from run_evals import sha256


class AuditEvidence(unittest.TestCase):
    def setUp(self):
        self.suite = json.dumps([{"id": "case-1", "request": "整理这段话", "input": "已核对。",
                                 "expectations": ["保留核对状态"], "rationale": "private hypothesis"}])
        self.manifest = {"suite_sha256": sha256(self.suite), "case_ids": ["case-1"],
                         "skill_commit": "private-revision"}

    def test_judge_receives_source_and_output_without_private_provenance(self):
        tasks = prepare(self.suite, self.manifest, {"case-1": "已核对。"})
        data = json.loads(tasks[0]["input"])
        self.assertEqual(data["input"], "已核对。")
        self.assertEqual(data["output"], "已核对。")
        self.assertEqual(data["expectations"], ["保留核对状态"])
        self.assertNotIn("private hypothesis", json.dumps(tasks))
        self.assertNotIn("private-revision", json.dumps(tasks))

    def test_changed_suite_or_missing_output_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.suite + " ", self.manifest, {"case-1": "已核对。"})
        with self.assertRaises(ValueError):
            prepare(self.suite, self.manifest, {})


if __name__ == "__main__":
    unittest.main()
