from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_006_retrospective_category(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PRet", "d", "o")
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("RT1", "2025-12-01", "2025-12-07", 10)
    res = sm.track_sprint_retrospective(sp["id"], ["ok"], ["bad"], ["imp"]) 
    assert res.get("sprint_id") == sp["id"]
