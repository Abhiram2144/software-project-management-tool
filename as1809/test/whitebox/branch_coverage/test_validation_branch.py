import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# White-box Testing Technique: Branch Coverage
# User Story: PRJ-004 (Validation and Error Handling)
# Sprint: 3
class TestValidationBranchCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_branch_owner_blank(self):
        with self.assertRaises(ValidationError):
            self.pm.create_project("Proj", "desc", "   ")

    def test_branch_title_duplicate(self):
        self.pm.create_project("Proj", "desc", "o")
        with self.assertRaises(ValidationError):
            self.pm.create_project("proj", "desc", "o2")

    def test_branch_points_invalid(self):
        proj = self.pm.create_project("Proj2", "desc", "o")
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(proj["id"], "Story", "desc", "bad")


if __name__ == "__main__":
    unittest.main()
