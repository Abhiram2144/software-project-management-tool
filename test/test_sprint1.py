import json
from pathlib import Path
import pytest

from src.project_manager.project_manager import ProjectManager


def test_create_project_success(tmp_path):
    data_file = tmp_path / "projects.json"
    pm = ProjectManager(data_file=str(data_file))

    proj = pm.create_project("Test Project", "A sample project", "Alice")
    assert proj["id"] == 1
    assert proj["title"] == "Test Project"

    # persisted file exists and contains project
    with open(data_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert len(data.get("projects", [])) == 1


def test_create_project_blank_title_raises(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    with pytest.raises(ValueError):
        pm.create_project("  ", "desc", "owner")


def test_create_project_duplicate_rejected(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    pm.create_project("P1", "d", "o")
    with pytest.raises(ValueError):
        pm.create_project("p1", "d2", "o2")  # case-insensitive duplicate


def test_list_projects_shows_summary(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    pm.create_project("Alpha", "a", "A")
    pm.create_project("Beta", "b", "B")
    lst = pm.list_projects()
    assert isinstance(lst, list)
    assert len(lst) == 2
    assert all("id" in p and "title" in p and "story_count" in p for p in lst)


def test_add_story_to_project_success(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    proj = pm.create_project("Proj", "d", "o")
    sid = pm.add_story_to_project(proj["id"], title="Story 1", description="sdesc", points=5)
    assert sid["id"] == 1
    # get project and verify story nested
    p = pm._find_project(proj["id"])
    assert len(p["stories"]) == 1
    assert p["stories"][0]["title"] == "Story 1"


def test_add_story_blank_title_and_project_missing(tmp_path):
    pm = ProjectManager(data_file=str(tmp_path / "projects.json"))
    # missing project
    with pytest.raises(ValueError):
        pm.add_story_to_project(999, title="S", description="d", points=1)

    # blank title
    proj = pm.create_project("X", "d", "o")
    with pytest.raises(ValueError):
        pm.add_story_to_project(proj["id"], title=" ", description="d", points=1)
