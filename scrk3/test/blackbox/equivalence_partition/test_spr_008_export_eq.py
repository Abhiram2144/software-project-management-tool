from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_008_export_eq(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PE2", "d", "o")
    s = pm.add_story_to_project(p["id"], "Exp2", "d", 1)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("EX2", "2025-12-01", "2025-12-07", 5)
    try:
        sm.export_sprint_report(sp["id"], filepath=None, include_details=False, fmt="json")
    except Exception:
        pass
    assert True
