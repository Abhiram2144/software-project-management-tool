import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager


# White-box Testing Technique: Statement Coverage
# User Stories: PRJ-003 (Save / Load), PRJ-004 (Validation logging paths)
# Sprint: 1
class TestSaveLoadStatementCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_save_then_load_statements(self):
        # cover save path with existing data
        self.pm.create_project("Proj", "desc", "owner")
        path = self.pm.save_project_data()
        self.assertTrue(os.path.exists(path))
        loaded = self.pm.load_project_data()
        self.assertEqual(len(loaded.get("projects", [])), 1)

    def test_load_when_file_missing_statements(self):
        # remove file to exercise missing-file branch
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        loaded = self.pm.load_project_data()
        self.assertIn("projects", loaded)


if __name__ == "__main__":
    unittest.main()
