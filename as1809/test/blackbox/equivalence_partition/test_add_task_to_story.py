import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Equivalence Partitioning
# User Story: TSK-001 (Add Task to Story)
# Sprint: 1
class TestAddTaskEquivalence(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "desc", "owner")
        self.story = self.pm.add_story_to_project(self.project["id"], "Story", "desc", 3)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_task_valid(self):
        task = self.pm.add_task_to_story(self.project["id"], self.story["id"], "Task 1", assigned_to="alice", estimated_hours=2)
        self.assertEqual(task["title"], "Task 1")
        self.assertEqual(task["assigned_to"], "alice")

    def test_blank_task_title_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.add_task_to_story(self.project["id"], self.story["id"], "   ")

    def test_duplicate_task_title_invalid(self):
        self.pm.add_task_to_story(self.project["id"], self.story["id"], "Task 1")
        with self.assertRaises(ValidationError):
            self.pm.add_task_to_story(self.project["id"], self.story["id"], "task 1")

    def test_negative_estimated_hours_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.add_task_to_story(self.project["id"], self.story["id"], "Task 2", estimated_hours=-5)


if __name__ == "__main__":
    unittest.main()
