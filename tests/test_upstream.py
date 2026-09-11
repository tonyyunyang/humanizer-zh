"""Behavioral tests for notifications and review state, with no network writes."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from check_upstream import BOT, MARKER, inspect_sources, load_lock, record_review, render_report, snapshot, sync_issue

OLD = "a" * 40
NEW = "b" * 40
TREE = "c" * 40
BLOB = "d" * 40
CHANGED = "e" * 40
SOURCE = {"id": "example", "repository": "owner/source", "branch": "main", "version": "1.0.0", "revision": OLD, "reviewed_on": "2026-09-11", "files": {"SKILL.md": BLOB}}
CHANGE = {"repository": "owner/source", "reviewed": OLD, "head": NEW, "paths": ["SKILL.md"]}


def remote(blob=BLOB, truncated=False, missing=False):
    api = Mock()
    api.request.side_effect = [
        {"sha": NEW, "commit": {"tree": {"sha": TREE}}},
        {"truncated": truncated, "tree": [] if missing else [{"path": "SKILL.md", "type": "blob", "sha": blob}]},
    ]
    return api


def issue(body=None, state="open", owner=BOT):
    return {"number": 7, "state": state, "body": render_report([CHANGE]) if body is None else body, "user": {"login": owner}}


class ContentTracking(unittest.TestCase):
    def test_unrelated_commit_does_not_trigger_review(self):
        self.assertEqual(inspect_sources(remote(), {"sources": [SOURCE]}), [])

    def test_changed_tracked_file_triggers_review(self):
        self.assertEqual(inspect_sources(remote(blob=CHANGED), {"sources": [SOURCE]}), [CHANGE])

    def test_removed_file_is_not_silently_ignored(self):
        self.assertEqual(inspect_sources(remote(missing=True), {"sources": [SOURCE]}), [CHANGE])

    def test_incomplete_tree_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            snapshot(remote(truncated=True), SOURCE, "main")

    def test_network_failure_is_not_reported_as_unchanged(self):
        api = Mock()
        api.request.side_effect = RuntimeError("GitHub HTTP 403")
        with self.assertRaisesRegex(RuntimeError, "403"):
            inspect_sources(api, {"sources": [SOURCE]})
        self.assertTrue(all(call.args[0] == "GET" for call in api.request.call_args_list))


class Notifications(unittest.TestCase):
    def test_same_diff_does_not_write_again(self):
        api = Mock()
        api.request.return_value = [issue()]
        sync_issue(api, "owner/target", [CHANGE])
        self.assertEqual(api.request.call_count, 1)

    def test_first_diff_creates_one_issue(self):
        api = Mock()
        api.request.return_value = []
        sync_issue(api, "owner/target", [CHANGE])
        self.assertEqual(api.request.call_count, 2)
        self.assertEqual(api.request.call_args.args[:2], ("POST", "/repos/owner/target/issues"))
        self.assertIn(MARKER, api.request.call_args.args[2]["body"])

    def test_new_diff_updates_existing_issue(self):
        api = Mock()
        api.request.return_value = [issue(body=MARKER + "\nPrevious changes")]
        sync_issue(api, "owner/target", [CHANGE])
        self.assertEqual(api.request.call_args.args[:2], ("PATCH", "/repos/owner/target/issues/7"))

    def test_closing_without_review_does_not_silence_changes(self):
        api = Mock()
        api.request.return_value = [issue(state="closed")]
        sync_issue(api, "owner/target", [CHANGE])
        self.assertEqual(api.request.call_args.args[2], {"state": "open"})

    def test_resolved_changes_close_the_existing_issue(self):
        api = Mock()
        api.request.return_value = [issue()]
        sync_issue(api, "owner/target", [])
        self.assertEqual(api.request.call_args.args[2], {"state": "closed"})

    def test_clean_state_without_issue_never_creates_one(self):
        api = Mock()
        api.request.return_value = []
        sync_issue(api, "owner/target", [])
        self.assertEqual(api.request.call_count, 1)

    def test_human_owned_issue_is_not_modified(self):
        api = Mock()
        api.request.return_value = [issue(owner="contributor")]
        sync_issue(api, "owner/target", [CHANGE])
        self.assertEqual(api.request.call_args.args[0], "POST")

    def test_finds_older_issue_after_first_page(self):
        api = Mock()
        api.request.side_effect = [[issue(owner="contributor")] * 100, [issue()]]
        sync_issue(api, "owner/target", [CHANGE])
        self.assertEqual(api.request.call_count, 2)
        self.assertIn("page=2", api.request.call_args.args[1])


class ReviewRecord(unittest.TestCase):
    def test_record_changes_only_the_reviewed_source(self):
        other = dict(SOURCE, id="other", repository="owner/other")
        lock = {"schema_version": 1, "sources": [copy.deepcopy(SOURCE), other]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock.json"
            record_review(remote(blob=CHANGED), path, lock, "example", NEW)
            saved = load_lock(path)
        self.assertEqual(saved["sources"][0]["revision"], NEW)
        self.assertEqual(saved["sources"][0]["files"]["SKILL.md"], CHANGED)
        self.assertEqual(saved["sources"][1], other)

    def test_removed_path_does_not_overwrite_review_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock.json"
            original = json.dumps({"schema_version": 1, "sources": [SOURCE]})
            path.write_text(original)
            with self.assertRaisesRegex(ValueError, "removed/renamed"):
                record_review(remote(missing=True), path, json.loads(original), "example", NEW)
            self.assertEqual(path.read_text(), original)

    def test_record_requires_exact_commit_not_moving_branch(self):
        with self.assertRaisesRegex(ValueError, "40-character"):
            record_review(Mock(), Path("unused"), {"sources": [SOURCE]}, "example", "main")


if __name__ == "__main__":
    unittest.main()
