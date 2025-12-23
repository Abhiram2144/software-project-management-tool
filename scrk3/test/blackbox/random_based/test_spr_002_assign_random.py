from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_002_random_assign(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PR", "d", "o")
    s = pm.add_story_to_project(p["id"], "St", "d", 2)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("R1", "2025-12-01", "2025-12-07", 5)
    res = sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    assert res["sprint_id"] == sp["id"]
