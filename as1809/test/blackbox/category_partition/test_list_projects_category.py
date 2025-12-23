import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager


# Black-box Testing Technique: Category Partition
# User Story: PRJ-002 (View All Projects)
# Sprint: 1
class TestListProjectsCategory(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_list_projects_empty(self):
        projects = self.pm.list_projects()
        self.assertEqual(projects, [])

    def test_list_projects_after_creation(self):
        self.pm.create_project("Proj1", "d1", "o1")
        self.pm.create_project("Proj2", "d2", "o2")
        projects = self.pm.list_projects()
        ids = sorted(p["id"] for p in projects)
        self.assertEqual(ids, [1, 2])
        titles = {p["title"] for p in projects}
        self.assertEqual(titles, {"Proj1", "Proj2"})


if __name__ == "__main__":
    unittest.main()
