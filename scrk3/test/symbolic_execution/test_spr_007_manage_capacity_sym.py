from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_007_manage_capacity(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PC", "d", "o")
    s = pm.add_story_to_project(p["id"], "A", "d", 5)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("Cap", "2025-12-01", "2025-12-14", 20)
    sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    out = sm.manage_sprint_capacity(sp["id"], {"alice": 10})
    assert isinstance(out, dict)
