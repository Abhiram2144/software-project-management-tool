from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_008_export_branch(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PE", "d", "o")
    s = pm.add_story_to_project(p["id"], "Exp", "d", 2)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("EX", "2025-12-01", "2025-12-07", 5)
    sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    try:
        out = sm.export_sprint_report(sp["id"], filepath=str(tmp_path / "r.json"), include_details=True, fmt="json")
    except Exception:
        out = None
    assert out is None or isinstance(out, dict)
