import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# White-box Testing Technique: Path Coverage
# User Stories: PRJ-004, STY-003, TSK-002
# Sprint: 1
class TestPathCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)
        self.project = self.pm.create_project("Proj", "desc", "owner")
        # story with tasks to exercise task completion paths
        self.story_with_task = self.pm.add_story_to_project(self.project["id"], "Story", "desc", 2)
        self.task = self.pm.add_task_to_story(self.project["id"], self.story_with_task["id"], "Task")
        # story without tasks to exercise deletion success path
        self.story_no_task = self.pm.add_story_to_project(self.project["id"], "Archive Story", "desc", 2)

    def tearDown(self):
        self.tmpdir.cleanup()

    # Path P1: project exists AND story exists -> delete success
    def test_path_delete_story_success(self):
        deleted = self.pm.delete_story(self.project["id"], self.story_no_task["id"])
        self.assertEqual(deleted["id"], self.story_no_task["id"])

    # Path P2: project exists AND story missing -> error
    def test_path_delete_story_missing(self):
        with self.assertRaises(ValidationError):
            self.pm.delete_story(self.project["id"], 12345)

    # Path P3: task already complete -> no-op branch
    def test_path_task_already_complete(self):
        self.pm.mark_task_complete(self.project["id"], self.story_with_task["id"], self.task["id"])
        result = self.pm.mark_task_complete(self.project["id"], self.story_with_task["id"], self.task["id"])
        self.assertIn("notes", result)

    # Path P4: task not complete -> update branch
    def test_path_task_complete_first_time(self):
        result = self.pm.mark_task_complete(self.project["id"], self.story_with_task["id"], self.task["id"], by="alice")
        self.assertEqual(result["status"], "done")


if __name__ == "__main__":
    unittest.main()
