"""Test evidence isolation and failure accounting, not Chinese quality scores."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_evals import command, make_prompt, parse_events, select_cases
from make_blind_pairs import prepare


class EvaluationIsolation(unittest.TestCase):
    def test_editor_does_not_receive_answers_or_partition(self):
        prompt = make_prompt({"id": "case-1", "request": "润色", "input": "原文",
                              "sample": "样文", "expectations": ["secret criterion"],
                              "partition": "holdout", "rationale": "secret rationale"}, "规范")
        self.assertIn("样文", prompt)
        self.assertIn("原文", prompt)
        self.assertNotIn("secret", prompt)
        self.assertNotIn("holdout", prompt)

    def test_complete_event_does_not_erase_failure(self):
        result = parse_events('\n'.join(json.dumps(e) for e in [
            {"type": "error", "message": "transport failed"},
            {"type": "turn.completed", "usage": {"input_tokens": 10}},
        ]))
        self.assertEqual(result["errors"], ["transport failed"])
        self.assertTrue(result["completed"])

    def test_unexpected_tools_are_recorded(self):
        result = parse_events(json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "command": "echo unexpected"}}))
        self.assertEqual(result["tools_used"], ["command_execution"])

    def test_partial_or_malformed_events_cannot_count_as_complete(self):
        result = parse_events('{"type":"turn.started"}\nnot-json')
        self.assertFalse(result["completed"])
        self.assertTrue(result["errors"])

    def test_per_case_command_is_ephemeral_and_read_only(self):
        args = command("test-model", "max", Path("/tmp/test-evaluation"))
        self.assertIn("--ignore-user-config", args)
        self.assertIn("--ephemeral", args)
        self.assertEqual(args[args.index("--sandbox") + 1], "read-only")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", args)

    def test_partition_and_selection_fail_on_typo(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps([
                {"id": "case-1", "request": "润色", "input": "一", "partition": "development"},
                {"id": "case-2", "request": "润色", "input": "二", "partition": "holdout"},
            ]))
            selected = select_cases(path, [], [], "holdout")
            self.assertEqual([c["id"] for c in selected], ["case-2"])
            with self.assertRaises(ValueError):
                select_cases(path, ["case-typo"], [], None)

    def test_blind_tasks_hide_revision_identity(self):
        suite = [{"id": "case-1", "request": "润色", "input": "原文", "expectations": ["保留事实"]}]
        common = {"model": "test-model", "effort": "max", "suite_sha256": "suite",
                  "case_ids": ["case-1"], "partition": None, "cli_version": "1",
                  "runner_sha256": "runner", "timeout_seconds": 180, "schema_sha256": None}
        first = {**common, "skill_commit": "baseline-secret-revision"}
        second = {**common, "skill_commit": "candidate-secret-revision"}
        tasks, mapping = prepare(suite, first, {"case-1": "改稿甲"}, second, {"case-1": "改稿乙"}, 19)
        serialized = json.dumps(tasks, ensure_ascii=False)
        self.assertNotIn("secret-revision", serialized)
        self.assertIn("保留事实", serialized)
        material = json.loads(tasks[0]["input"])
        source = {"first": "改稿甲", "second": "改稿乙"}
        self.assertEqual(material["A"], source[mapping["case-1"]["A"]])
        self.assertEqual(material["B"], source[mapping["case-1"]["B"]])

    def test_changed_execution_settings_cannot_be_silently_compared(self):
        common = {"model": "a", "effort": "max", "suite_sha256": "suite",
                  "case_ids": [], "partition": None, "cli_version": "1",
                  "runner_sha256": "runner", "timeout_seconds": 180, "schema_sha256": None}
        for field, changed in [("model", "b"), ("cli_version", "2"),
                               ("runner_sha256", "different-runner"), ("timeout_seconds", 360)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                prepare([], common, {}, {**common, field: changed}, {}, 1)


if __name__ == "__main__":
    unittest.main()
