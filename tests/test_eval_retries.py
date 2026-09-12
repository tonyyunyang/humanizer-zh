import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from complete_eval_run import select_results


class RetryEvidence(unittest.TestCase):
    def batch(self, root, name, status, prompt="same", model="test"):
        folder = root / name
        folder.mkdir()
        manifest = {"status": "complete" if status == "ok" else "incomplete",
                    "case_ids": ["case-1"], "total_runs": 1, "repeats": 1,
                    "skill_commit": "commit", "skill_sha256": "skill", "suite_sha256": "suite",
                    "model": model, "effort": "max", "cli_version": "1", "runner_sha256": "runner",
                    "schema_sha256": None, "timeout_seconds": 240, "partition": "holdout"}
        (folder / "manifest.json").write_text(json.dumps(manifest))
        (folder / "case-1-1.json").write_text(json.dumps({"status": status, "prompt_sha256": prompt}))
        return folder

    def test_failed_execution_can_be_completed_without_erasing_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = self.batch(root, "base", "invalid")
            retry = self.batch(root, "retry", "ok")
            _, selected, failed, attempts = select_results(base, [retry])
            self.assertEqual(selected["case-1"], retry / "case-1-1.json")
            self.assertEqual(failed, [str(base / "case-1-1.json")])
            self.assertEqual(attempts, 2)
            self.assertEqual(json.loads((base / "manifest.json").read_text())["status"], "incomplete")

    def test_successful_output_cannot_be_cherry_picked_away(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                select_results(self.batch(root, "base", "ok"), [self.batch(root, "retry", "ok")])

    def test_changed_prompt_or_model_is_rejected(self):
        for changed in [{"prompt": "different"}, {"model": "different"}]:
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaises(ValueError):
                    select_results(self.batch(root, "base", "invalid"),
                                   [self.batch(root, "retry", "ok", **changed)])


if __name__ == "__main__":
    unittest.main()
