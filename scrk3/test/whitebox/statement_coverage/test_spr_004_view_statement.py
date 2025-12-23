from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_004_view_statement(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PV", "d", "o")
    s = pm.add_story_to_project(p["id"], "A", "d", 2)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("VS", "2025-12-01", "2025-12-07", 10)
    sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    summary = sm.view_sprint_summary(sp["id"])
    assert summary.get("sprint_id") == sp["id"]
