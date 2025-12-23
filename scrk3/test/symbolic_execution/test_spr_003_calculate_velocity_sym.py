from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_003_calculate_velocity_sym(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("P3", "d", "o")
    s = pm.add_story_to_project(p["id"], "A", "d", 3)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("CV", "2025-12-01", "2025-12-07", 10)
    sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    pm.get_story(p["id"], s["id"]) ["progress"] = 100.0
    pm.save_data()
    v = sm.calculate_velocity(sprint_id=sp["id"])
    assert v["velocity"] == 3.0
