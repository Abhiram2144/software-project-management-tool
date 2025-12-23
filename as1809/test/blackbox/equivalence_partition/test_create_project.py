import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Equivalence Partitioning
# User Story: PRJ-001 (Create New Project)
# Sprint: 1
class TestCreateProjectEquivalence(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_valid_project_creation(self):
        project = self.pm.create_project("Proj A", "desc", "owner1")
        self.assertEqual(project["title"], "Proj A")
        self.assertEqual(project["owner"], "owner1")

    def test_blank_title_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.create_project("   ", "desc", "owner1")

    def test_duplicate_title_invalid(self):
        self.pm.create_project("Proj A", "desc", "owner1")
        with self.assertRaises(ValidationError):
            self.pm.create_project("proj a", "desc2", "owner2")

    def test_missing_owner_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.create_project("Proj B", "desc", "")


if __name__ == "__main__":
    unittest.main()
