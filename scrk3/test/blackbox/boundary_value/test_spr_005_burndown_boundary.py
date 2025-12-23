from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_005_burndown_boundary(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PB", "d", "o")
    s = pm.add_story_to_project(p["id"], "B1", "d", 8)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("BD", "2025-12-01", "2025-12-02", 10)
    sm.add_story_to_sprint(p["id"], s["id"], sp["id"])
    chart = sm.generate_burndown_chart(sp["id"])
    assert "dates" in chart
