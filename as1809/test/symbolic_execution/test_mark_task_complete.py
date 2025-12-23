import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Symbolic Execution
# Path Condition: project_id valid AND story_id valid AND task complete vs not complete
# User Story: TSK-002
# Sprint: 1
class TestSymbolicMarkTaskComplete(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "d", "owner")
        self.story = self.pm.add_story_to_project(self.project["id"], "Story", "d", 1)
        self.task = self.pm.add_task_to_story(self.project["id"], self.story["id"], "Task")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_path_first_completion(self):
        result = self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"], by="bob")
        self.assertEqual(result["status"], "done")

    def test_path_task_missing(self):
        with self.assertRaises(ValidationError):
            self.pm.mark_task_complete(self.project["id"], self.story["id"], 999)

    def test_path_already_complete(self):
        self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"])
        result = self.pm.mark_task_complete(self.project["id"], self.story["id"], self.task["id"])
        self.assertIn("notes", result)


if __name__ == "__main__":
    unittest.main()
