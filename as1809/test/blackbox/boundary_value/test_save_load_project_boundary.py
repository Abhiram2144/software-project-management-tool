import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager


# Black-box Testing Technique: Boundary Value Analysis
# User Story: PRJ-003 (Save / Load Project Data)
# Sprint: 1
class TestSaveLoadBoundary(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_save_and_load_empty_store(self):
        path = self.pm.save_project_data()
        self.assertTrue(os.path.exists(path))
        loaded = self.pm.load_project_data()
        self.assertIn("projects", loaded)

    def test_save_and_load_with_project(self):
        self.pm.create_project("Proj", "desc", "owner")
        self.pm.save_project_data()
        loaded = self.pm.load_project_data()
        self.assertEqual(len(loaded.get("projects", [])), 1)

    def test_load_restore_missing_file(self):
        # delete the file to force fallback
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        loaded = self.pm.load_project_data()
        self.assertIn("projects", loaded)


if __name__ == "__main__":
    unittest.main()
