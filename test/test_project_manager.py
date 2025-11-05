import json
import os
from pathlib import Path
import pytest

from src import ProjectManager


def test_create_project_and_list(tmp_path):
    data_file = tmp_path / "projects.json"
    pm = ProjectManager(data_file=str(data_file))

    # initially empty
    assert pm.list_projects() == []

    p = pm.create_project(title="My Project", description="desc", owner="owner")
    assert p["title"] == "My Project"
    assert p["id"] == 1

    # listing shows one project summary
    lst = pm.list_projects()
    assert len(lst) == 1
    assert lst[0]["story_count"] == 0

    # duplicate title should raise
    with pytest.raises(ValueError):
        pm.create_project(title="My Project", description="x", owner="y")


def test_add_edit_delete_story_and_persistence(tmp_path):
    data_file = tmp_path / "projects.json"
    pm = ProjectManager(data_file=str(data_file))
    project = pm.create_project("P2", "d", "o")
    pid = project["id"]

    story = pm.add_story_to_project(pid, title="S1", description="sdesc", points=5)
    assert story["id"] == 1
    assert story["points"] == 5

    # edit story
    edited = pm.edit_story(pid, story_id=1, description="newdesc", points=8)
    assert edited["description"] == "newdesc"
    assert edited["points"] == 8

    # save and load a new manager from the same file
    pm2 = ProjectManager(data_file=str(data_file))
    proj2 = pm2.get_project(pid)
    assert len(proj2["stories"]) == 1

    # delete story
    pm2.delete_story(pid, story_id=1)
    proj3 = pm2.get_project(pid)
    assert len(proj3["stories"]) == 0


def test_add_task_and_mark_complete_updates_progress(tmp_path):
    data_file = tmp_path / "projects.json"
    pm = ProjectManager(data_file=str(data_file))
    project = pm.create_project("P3", "d", "o")
    pid = project["id"]
    story = pm.add_story_to_project(pid, title="S2", description="sdesc", points=3)
    sid = story["id"]

    t1 = pm.add_task_to_story(pid, sid, title="T1", assigned_to="Dev", estimated_hours=2)
    t2 = pm.add_task_to_story(pid, sid, title="T2", assigned_to="Dev2", estimated_hours=1)

    s = pm.get_story(pid, sid)
    assert s["progress"] == 0.0

    pm.mark_task_complete(pid, sid, "T1")
    s2 = pm.get_story(pid, sid)
    assert any(t["status"] == "done" for t in s2["tasks"])
    assert s2["progress"] == 50.0

    pm.mark_task_complete(pid, sid, "T2")
    s3 = pm.get_story(pid, sid)
    assert s3["progress"] == 100.0


def test_invalid_operations_raise(tmp_path):
    data_file = tmp_path / "projects.json"
    pm = ProjectManager(data_file=str(data_file))

    with pytest.raises(ValueError):
        pm.create_project("", "d", "o")

    p = pm.create_project("Valid", "d", "o")
    with pytest.raises(ValueError):
        pm.add_story_to_project(999, "x", "d", 1)

    with pytest.raises(ValueError):
        pm.add_task_to_story(p["id"], 999, "t")

    with pytest.raises(ValueError):
        pm.mark_task_complete(p["id"], 999, "t")
