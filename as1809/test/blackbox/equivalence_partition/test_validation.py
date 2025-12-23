import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Equivalence Partitioning
# User Story: PRJ-004 (Validation & Error Handling)
# Sprint: 3
class TestValidationEquivalence(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_missing_title_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.pm.create_project(None, "desc", "owner")

    def test_blank_owner_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.pm.create_project("Proj", "desc", "   ")

    def test_invalid_points_type_raises_validation_error(self):
        proj = self.pm.create_project("Proj", "desc", "owner")
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(proj["id"], "Story", "desc", "abc")


if __name__ == "__main__":
    unittest.main()
