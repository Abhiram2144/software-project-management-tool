from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_002_branch(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PR2", "d", "o")
    s = pm.add_story_to_project(p["id"], "St2", "d", 4)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("R2", "2025-12-01", "2025-12-07", 5)
    sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    summary = sm.view_sprint_summary(sp["id"])
    assert summary["sprint_id"] == sp["id"]
