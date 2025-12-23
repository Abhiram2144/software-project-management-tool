from src.project_manager.project_manager import ProjectManager
from src.sprint_manager import SprintManager


def test_spr_005_burndown_path(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("PB2", "d", "o")
    s = pm.add_story_to_project(p["id"], "B2", "d", 1)
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("BD2", "2025-12-01", "2025-12-01", 1)
    chart = sm.generate_burndown_chart(sp["id"])
    assert isinstance(chart.get("ideal_remaining"), list)
