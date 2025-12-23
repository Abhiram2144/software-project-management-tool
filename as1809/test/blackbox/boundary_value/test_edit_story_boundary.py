import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Boundary Value Analysis
# User Story: STY-002 (Edit / Update User Story)
# Sprint: 1
class TestEditStoryBoundary(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "desc", "owner")
        self.story = self.pm.add_story_to_project(self.project["id"], "Story", "desc", 0)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_boundary_zero_points_valid(self):
        updated = self.pm.edit_story(self.project["id"], self.story["id"], points=0)
        self.assertEqual(updated["points"], 0)

    def test_boundary_negative_points_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.edit_story(self.project["id"], self.story["id"], points=-1)

    def test_boundary_long_description_truncated(self):
        long_desc = "x" * 1200
        updated = self.pm.edit_story(self.project["id"], self.story["id"], description=long_desc)
        self.assertTrue(len(updated["description"]) <= 1003)


if __name__ == "__main__":
    unittest.main()
