import json
from pathlib import Path
import pytest
from src.sprint_manager import SprintManager
from src.project_manager.project_manager import ProjectManager


def test_create_sprint_success(tmp_path):
    sf = tmp_path / "sprints.json"
    sm = SprintManager(data_file=str(sf))
    sp = sm.create_sprint("Sprint 1", "2025-11-01", "2025-11-14", 80)
    assert sp["id"] == 1
    assert sp["name"] == "Sprint 1"
    assert sp["capacity"] == 80
    # persisted
    with open(sf, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert len(data.get("sprints", [])) == 1


def test_add_story_to_sprint_and_velocity(tmp_path):
    # prepare project and story
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    proj = pm.create_project("P", "d", "o")
    story = pm.add_story_to_project(proj["id"], "S1", "desc", 5)

    # prepare sprint
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("S1", "2025-11-01", "2025-11-07", 40)

    # add story
    res = sm.add_story_to_sprint(proj["id"], story["id"], sp["id"])
    assert res["sprint_id"] == sp["id"]

    # story initially not complete -> velocity 0
    v = sm.calculate_velocity(sprint_id=sp["id"])
    assert v["velocity"] == 0.0

    # mark taskless story as complete by setting progress
    p = pm.get_story(proj["id"], story["id"])
    p["progress"] = 100.0
    pm.save_data()

    v2 = sm.calculate_velocity(sprint_id=sp["id"])
    assert v2["velocity"] == 5.0


def test_calculate_average_velocity(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    p = pm.create_project("P2", "d", "o")
    s1 = pm.add_story_to_project(p["id"], "A", "d", 3)
    s2 = pm.add_story_to_project(p["id"], "B", "d", 5)

    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp1 = sm.create_sprint("SP1", "2025-01-01", "2025-01-14", 40)
    sp2 = sm.create_sprint("SP2", "2025-02-01", "2025-02-14", 40)

    sm.add_story_to_sprint(p["id"], s1["id"], sp1["id"])
    sm.add_story_to_sprint(p["id"], s2["id"], sp2["id"])

    # mark s1 complete
    pm.get_story(p["id"], s1["id"]) ["progress"] = 100.0
    # leave s2 incomplete
    pm.save_data()

    avg = sm.calculate_velocity(last_n=2)
    # only one completed story points=3 over 2 sprints -> average 1.5
    assert avg["velocity"] == pytest.approx(1.5)
