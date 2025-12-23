import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# White-box Testing Technique: Branch Coverage
# User Story: TSK-002 (Mark Task Complete)
# Sprint: 1
class TestMarkTaskCompleteBranch(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "desc", "owner")
        self.story = self.pm.add_story_to_project(self.project["id"], "Story", "desc", 1)
        self.task = self.pm.add_task_to_story(self.project["id"], self.story["id"], "Task", assigned_to="bob")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_branch_already_done_no_force(self):
        self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"], by="bob")
        result = self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"], by="bob")
        self.assertIn("notes", result)

    def test_branch_cascade_subtasks(self):
        # add subtasks to exercise cascade branch
        self.task.setdefault("subtasks", []).append({"title": "sub", "status": "open"})
        result = self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"], cascade=True)
        self.assertEqual(result["status"], "done")

    def test_branch_task_not_found(self):
        with self.assertRaises(ValidationError):
            self.pm.mark_task_complete(self.project["id"], self.story["id"], 999)


if __name__ == "__main__":
    unittest.main()
