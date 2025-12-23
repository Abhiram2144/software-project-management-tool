import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Symbolic Execution
# Path Condition: project title non-empty AND owner non-empty
# User Story: PRJ-001
# Sprint: 1
class TestSymbolicCreateProject(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_path_valid(self):
        proj = self.pm.create_project("Alpha", "d", "owner")
        self.assertEqual(proj["title"], "Alpha")

    def test_path_invalid_title(self):
        with self.assertRaises(ValidationError):
            self.pm.create_project("", "d", "owner")


if __name__ == "__main__":
    unittest.main()
