#!/usr/bin/env python3
"""Test suite for Task Journal."""

import unittest
import tempfile
import json
from pathlib import Path
from task_journal import TaskJournal


class TestTaskJournal(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.journal = TaskJournal(data_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_task(self):
        task = self.journal.add_task("Test task", ["test"])
        self.assertEqual(task["description"], "Test task")
        self.assertEqual(task["tags"], ["test"])
        self.assertFalse(task["completed"])

    def test_persistence(self):
        self.journal.add_task("Persistent task", ["data"])
        journal2 = TaskJournal(data_dir=self.temp_dir.name)
        self.assertEqual(len(journal2.tasks), 1)
        self.assertEqual(journal2.tasks[0]["description"], "Persistent task")

    def test_complete_task(self):
        task = self.journal.add_task("Complete me", ["test"])
        completed = self.journal.complete_task(task["id"])
        self.assertTrue(completed["completed"])
        self.assertIn("completed_at", completed)

    def test_complete_nonexistent_task(self):
        result = self.journal.complete_task(999)
        self.assertIsNone(result)

    def test_search_by_description(self):
        self.journal.add_task("Buy milk", ["personal"])
        self.journal.add_task("Buy bread", ["personal"])
        self.journal.add_task("Fix bug", ["work"])
        results = self.journal.search("buy")
        self.assertEqual(len(results), 2)

    def test_search_by_tag(self):
        self.journal.add_task("Task 1", ["work"])
        self.journal.add_task("Task 2", ["personal"])
        self.journal.add_task("Task 3", ["work", "urgent"])
        results = self.journal.search("", "work")
        self.assertEqual(len(results), 2)

    def test_search_combined(self):
        self.journal.add_task("Fix bug", ["work"])
        self.journal.add_task("Fix typo", ["personal"])
        results = self.journal.search("fix", "work")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["description"], "Fix bug")

    def test_report_metrics(self):
        self.journal.add_task("Task 1", ["work"])
        self.journal.add_task("Task 2", ["work"])
        self.journal.complete_task(1)
        report = self.journal.get_report(days=1)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["completed"], 1)
        self.assertEqual(report["pending"], 1)
        self.assertEqual(report["completion_rate"], "50%")

    def test_report_tag_filter(self):
        self.journal.add_task("Work task", ["work"])
        self.journal.add_task("Personal task", ["personal"])
        report = self.journal.get_report(days=1, tag_filter="work")
        self.assertEqual(report["total"], 1)

    def test_list_order(self):
        self.journal.add_task("First", ["test"])
        self.journal.add_task("Second", ["test"])
        tasks = self.journal.list_all()
        self.assertEqual(tasks[0]["description"], "Second")
        self.assertEqual(tasks[1]["description"], "First")

    def test_list_limit(self):
        for i in range(5):
            self.journal.add_task(f"Task {i}", ["test"])
        tasks = self.journal.list_all(limit=3)
        self.assertEqual(len(tasks), 3)


if __name__ == "__main__":
    unittest.main()
