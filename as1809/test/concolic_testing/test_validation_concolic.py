import os
import tempfile
import unittest
from src.project_manager.project_manager import ProjectManager, ValidationError


# Concolic Testing
# Initial Input: title="Proj", owner="owner"
# Negated Condition: owner blank
# User Story: PRJ-004
# Sprint: 3
class TestConcolicValidation(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmpdir.name, "projects.json")
        self.pm = ProjectManager(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_concolic_owner_present_then_blank(self):
        # concrete path: valid owner
        proj = self.pm.create_project("Proj", "d", "owner")
        self.assertEqual(proj["title"], "Proj")
        # negated condition: blank owner triggers ValidationError
        with self.assertRaises(ValidationError):
            self.pm.create_project("Proj2", "d", "   ")


if __name__ == "__main__":
    unittest.main()
