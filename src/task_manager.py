"""
task_manager.py
Thin wrapper functions for task operations. Delegates to ProjectManager so
that tasks live under stories in the canonical JSON store.
"""
from typing import List, Dict, Optional

from .project_manager import ProjectManager

_pm = ProjectManager()


def create_task(project_id: int, story_id: int, title: str, assigned_to: Optional[str] = None, estimated_hours: Optional[float] = None) -> Dict:
    """Create a new task under the given story. Returns the created task dict."""
    return _pm.add_task_to_story(project_id, story_id, title=title, assigned_to=assigned_to, estimated_hours=estimated_hours)


def mark_task_complete(project_id: int, story_id: int, task_title: str) -> Dict:
    """Mark a task (by title) as complete and update story progress."""
    return _pm.mark_task_complete(project_id, story_id, task_title)


def calculate_task_progress(project_id: int, story_id: int) -> float:
    """Return the progress percentage for the given story's tasks."""
    s = _pm.get_story(project_id, story_id)
    return float(s.get("progress", 0.0))


def list_all_tasks(project_id: Optional[int] = None) -> List[Dict]:
    """List tasks across all projects or for a single project."""
    tasks = []
    if project_id is None:
        for p in _pm._data.get("projects", []):
            for s in p.get("stories", []):
                for t in s.get("tasks", []):
                    tasks.append(t)
    else:
        proj = _pm.get_project(project_id)
        for s in proj.get("stories", []):
            for t in s.get("tasks", []):
                tasks.append(t)
    return tasks
