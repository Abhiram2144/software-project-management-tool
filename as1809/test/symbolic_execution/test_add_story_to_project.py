import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Symbolic Execution
# Path Condition: project_id valid AND story title unique AND points >= 0
# User Story: STY-001
# Sprint: 1
class TestSymbolicAddStory(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "d", "owner")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_path_valid(self):
        story = self.pm.add_story_to_project(self.project["id"], "Story", "d", 1)
        self.assertEqual(story["title"], "Story")

    def test_path_invalid_project(self):
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(999, "Story", "d", 1)

    def test_path_negative_points(self):
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(self.project["id"], "Bad", "d", -5)


if __name__ == "__main__":
    unittest.main()
