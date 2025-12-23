import os
import random
import string
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Black-box Testing Technique: Random-Based Testing
# User Stories: PRJ-001, STY-001, TSK-001, PRJ-004
# Sprint: 1
class TestRandomBased(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _rand_text(self, n=8):
        return "".join(random.choice(string.ascii_letters) for _ in range(n))

    def test_random_projects_and_stories_do_not_crash(self):
        for _ in range(5):
            title = self._rand_text()
            owner = self._rand_text()
            proj = self.pm.create_project(title, "desc", owner)
            story_title = self._rand_text()
            self.pm.add_story_to_project(proj["id"], story_title, "desc", random.randint(0, 8))
        projects = self.pm.list_projects()
        self.assertTrue(len(projects) >= 5)

    def test_random_invalid_points_raise(self):
        proj = self.pm.create_project(self._rand_text(), "d", self._rand_text())
        with self.assertRaises(ValidationError):
            self.pm.add_story_to_project(proj["id"], self._rand_text(), "d", "not-a-number")


if __name__ == "__main__":
    unittest.main()
