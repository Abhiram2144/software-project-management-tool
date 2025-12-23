from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_009_equivalence(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("Proj", "d", "o")
    s = pm.add_story_to_project(p["id"], "T", "d", 5)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("Veq", "2025-12-01", "2025-12-07", 10)
    sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    pm.get_story(p["id"], s["id"]) ["progress"] = 100.0
    pm.save_data()
    res = sm.set_sprint_status(sp["id"], "Completed")
    assert "Average team velocity" in res["message"]
