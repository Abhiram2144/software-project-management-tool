import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Boundary Value Analysis
# User Story: TSK-002 (Mark Task Complete)
# Sprint: 1
class TestMarkTaskCompleteBoundary(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "desc", "owner")
        self.story = self.pm.add_story_to_project(self.project["id"], "Story", "desc", 1)
        self.task = self.pm.add_task_to_story(self.project["id"], self.story["id"], "Task", estimated_hours=0)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_mark_complete_normal(self):
        result = self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"], by="alice")
        self.assertEqual(result["status"], "done")
        self.assertIn("completed_at", result)

    def test_mark_complete_already_done_no_force(self):
        self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"])
        result = self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"])
        self.assertIn("notes", result)

    def test_missing_task_identifier_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.mark_task_complete(self.project["id"], self.story["id"], None)


if __name__ == "__main__":
    unittest.main()
