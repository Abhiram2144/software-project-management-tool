import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Symbolic Execution
# Path Condition: project exists AND story exists AND new title non-blank
# User Story: STY-002
# Sprint: 1
class TestSymbolicEditStory(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "d", "owner")
        self.story = self.pm.add_story_to_project(self.project["id"], "Story", "d", 2)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_path_valid_title_change(self):
        updated = self.pm.edit_story(self.project["id"], self.story["id"], title="New Title")
        self.assertEqual(updated["title"], "New Title")

    def test_path_story_missing(self):
        with self.assertRaises(ValidationError):
            self.pm.edit_story(self.project["id"], 999, title="X")

    def test_path_blank_title(self):
        with self.assertRaises(ValidationError):
            self.pm.edit_story(self.project["id"], self.story["id"], title="   ")


if __name__ == "__main__":
    unittest.main()
