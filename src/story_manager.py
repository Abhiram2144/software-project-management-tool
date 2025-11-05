"""
story_manager.py
Wrapper functions for story-related operations. These delegate to the
central `ProjectManager` so that persistence and schema remain consistent.

Functions here are intended for other modules (sprint manager, CLI, metrics)
to import and use without instantiating ProjectManager directly.
"""
from typing import List, Dict, Optional

from .project_manager import ProjectManager

# Default manager instance (uses data/projects.json by default)
_pm = ProjectManager()


def add_user_story(project_id: int, title: str, description: str, story_points: int) -> Dict:
    """Add a new user story to the given project.

    Raises ValueError for invalid input. Returns the created story dict.
    """
    return _pm.add_story_to_project(project_id, title=title, description=description, points=story_points)


def assign_story_to_sprint(project_id: int, story_id: int, sprint_id: int) -> Dict:
    """Assign a story to a sprint by storing `sprint_id` on the story.

    This is a light-weight implementation so the Sprint Manager can call it
    without depending on sprint module internals.
    """
    proj = _pm.get_project(project_id)
    for s in proj.get("stories", []):
        if s.get("id") == story_id:
            s["sprint_id"] = sprint_id
            s["modified_at"] = _pm._now_iso() if hasattr(_pm, "_now_iso") else s.get("modified_at")
            proj["modified_at"] = s.get("modified_at")
            _pm.save_data()
            return s
    raise ValueError("Story not found")


def update_story_status(project_id: int, story_id: int, status: str) -> Dict:
    """Update the status of a story (e.g., 'todo', 'in-progress', 'done')."""
    proj = _pm.get_project(project_id)
    for s in proj.get("stories", []):
        if s.get("id") == story_id:
            s["status"] = status
            s["modified_at"] = _pm._now_iso() if hasattr(_pm, "_now_iso") else s.get("modified_at")
            proj["modified_at"] = s.get("modified_at")
            _pm.save_data()
            return s
    raise ValueError("Story not found")


def list_user_stories(project_id: Optional[int] = None) -> List[Dict]:
    """Return stories for a specific project or all stories across projects."""
    out = []
    if project_id is None:
        for p in _pm._data.get("projects", []):
            for s in p.get("stories", []):
                out.append(s)
    else:
        proj = _pm.get_project(project_id)
        out = list(proj.get("stories", []))
    return out
