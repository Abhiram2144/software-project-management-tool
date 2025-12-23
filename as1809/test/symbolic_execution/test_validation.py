import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Symbolic Execution
# Path Condition: invalid inputs trigger ValidationError
# User Story: PRJ-004
# Sprint: 3
class TestSymbolicValidation(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_path_missing_owner(self):
        with self.assertRaises(ValidationError):
            self.pm.create_project("Proj", "d", None)

    def test_path_invalid_points(self):
        proj = self.pm.create_project("Proj", "d", "owner")
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(proj["id"], "Story", "d", "bad")


if __name__ == "__main__":
    unittest.main()
