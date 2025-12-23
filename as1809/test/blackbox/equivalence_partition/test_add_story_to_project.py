import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Equivalence Partitioning
# User Story: STY-001 (Add User Story)
# Sprint: 1
class TestAddStoryEquivalence(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "desc", "owner")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_story_valid(self):
        story = self.pm.add_story_to_project(self.project["id"], "Story 1", "desc", 5)
        self.assertEqual(story["title"], "Story 1")
        self.assertEqual(story["points"], 5)

    def test_blank_story_title_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(self.project["id"], "   ", "desc", 3)

    def test_negative_points_invalid(self):
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(self.project["id"], "Story 2", "desc", -1)

    def test_duplicate_story_title_invalid(self):
        self.pm.add_story_to_project(self.project["id"], "Story 1", "desc", 3)
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(self.project["id"], "story 1", "desc2", 4)


if __name__ == "__main__":
    unittest.main()
