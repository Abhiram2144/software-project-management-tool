import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Category Partition
# User Story: STY-003 (Delete User Story)
# Sprint: 1
class TestDeleteStoryCategory(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "desc", "owner")
        self.story = self.pm.add_story_to_project(self.project["id"], "Story", "desc", 3)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_delete_existing_story(self):
        deleted = self.pm.delete_story(self.project["id"], self.story["id"])
        self.assertEqual(deleted["id"], self.story["id"])

    def test_delete_missing_story_category_not_found(self):
        with self.assertRaises(ValidationError):
            self.pm.delete_story(self.project["id"], 999)

    def test_delete_story_with_tasks_requires_cascade(self):
        self.pm.add_task_to_story(self.project["id"], self.story["id"], "Task")
        with self.assertRaises(ValidationError):
            self.pm.delete_story(self.project["id"], self.story["id"])


if __name__ == "__main__":
    unittest.main()
