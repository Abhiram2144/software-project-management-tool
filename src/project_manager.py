"""
project_manager.py
Handles creation, listing, and storage of software projects and user stories.

This module exposes the ProjectManager class which provides the following
capabilities required by the coursework:
 - create and list projects
 - add/edit/delete stories under a project
 - add tasks to stories and mark them complete
 - save/load JSON data to disk (data/projects.json by default)

All functions return plain Python dict/list structures suitable for other
modules to consume (Member B and C).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class Task:
    title: str
    assigned_to: Optional[str] = None
    status: str = "todo"
    estimated_hours: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Story:
    id: int
    title: str
    description: str
    points: int
    tasks: List[Dict[str, Any]]
    created_at: str
    modified_at: str
    progress: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class ProjectManager:
    """Manage projects, stories and tasks persisted as JSON.

    Usage:
      pm = ProjectManager(data_file="data/projects.json")
      pm.create_project(...)
      pm.add_story_to_project(...)
    """

    def __init__(self, data_file: Optional[str] = None):
        self.data_file = Path(data_file or "data/projects.json")
        self._data: Dict[str, Any] = {"projects": []}
        self.load_data()

    # ------------------ Persistence helpers ------------------
    def load_data(self) -> Dict[str, Any]:
        """Load data from the JSON file. If file missing, initialize empty store."""
        if not self.data_file.parent.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            # create an empty file
            self._data = {"projects": []}
            self.save_data()
            return self._data

        try:
            with self.data_file.open("r", encoding="utf-8") as fh:
                self._data = json.load(fh)
        except Exception:
            # If file is corrupt or unreadable, reset to safe empty structure
            self._data = {"projects": []}
            self.save_data()

        # Ensure schema keys exist
        if "projects" not in self._data or not isinstance(self._data["projects"], list):
            self._data["projects"] = []

        return self._data

    def save_data(self) -> None:
        """Persist current in-memory data to disk."""
        with self.data_file.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, ensure_ascii=False)

    # ------------------ Project operations ------------------
    def _next_project_id(self) -> int:
        ids = [p.get("id", 0) for p in self._data.get("projects", [])]
        return max(ids, default=0) + 1

    def create_project(self, title: str, description: str, owner: str) -> Dict[str, Any]:
        """Create a new project and persist it.

        Raises ValueError for blank titles or duplicate titles (case-insensitive).
        Returns the created project dict.
        """
        title = (title or "").strip()
        if not title:
            raise ValueError("Project title cannot be blank")

        # duplicate check
        for p in self._data.get("projects", []):
            if p.get("title", "").strip().lower() == title.lower():
                raise ValueError("Project title already exists")

        project = {
            "id": self._next_project_id(),
            "title": title,
            "description": description or "",
            "owner": owner or "",
            "stories": [],
            "created_at": _now_iso(),
            "modified_at": _now_iso(),
        }

        self._data.setdefault("projects", []).append(project)
        self.save_data()
        print(f"Project created: {project['id']} - {project['title']}")
        return project

    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Return a list of projects with summary fields (id, title, owner, story_count)."""
        out = []
        for p in self._data.get("projects", []):
            out.append(
                {
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "owner": p.get("owner"),
                    "story_count": len(p.get("stories", [])),
                }
            )
        return out

    def _find_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        for p in self._data.get("projects", []):
            if p.get("id") == project_id:
                return p
        return None

    # # ------------------ Story operations ------------------
    # def _next_story_id(self, project: Dict[str, Any]) -> int:
    #     ids = [s.get("id", 0) for s in project.get("stories", [])]
    #     return max(ids, default=0) + 1

    # def add_story_to_project(self, project_id: int, title: str, description: str, points: int) -> Dict[str, Any]:
    #     """Add a new story under the given project.

    #     Validates inputs and duplicate story titles within the project.
    #     Returns the created story dict.
    #     """
    #     title = (title or "").strip()
    #     if not title:
    #         raise ValueError("Story title cannot be blank")

    #     project = self._find_project(project_id)
    #     if project is None:
    #         raise ValueError("Project not found")

    #     for s in project.get("stories", []):
    #         if s.get("title", "").strip().lower() == title.lower():
    #             raise ValueError("Story title already exists in project")

    #     story = Story(
    #         id=self._next_story_id(project),
    #         title=title,
    #         description=description or "",
    #         points=int(points or 0),
    #         tasks=[],
    #         created_at=_now_iso(),
    #         modified_at=_now_iso(),
    #         progress=0.0,
    #     ).to_dict()

    #     project.setdefault("stories", []).append(story)
    #     project["modified_at"] = _now_iso()
    #     self.save_data()
    #     print(f"Story added to project {project_id}: {story['id']} - {story['title']}")
    #     return story

    # def edit_story(self, project_id: int, story_id: int, description: Optional[str] = None, points: Optional[int] = None) -> Dict[str, Any]:
    #     """Edit a story's description or points. Updates modified timestamp."""
    #     project = self._find_project(project_id)
    #     if project is None:
    #         raise ValueError("Project not found")

    #     for s in project.get("stories", []):
    #         if s.get("id") == story_id:
    #             if description is not None:
    #                 s["description"] = description
    #             if points is not None:
    #                 s["points"] = int(points)
    #             s["modified_at"] = _now_iso()
    #             project["modified_at"] = _now_iso()
    #             self.save_data()
    #             return s

    #     raise ValueError("Story not found")

    # def delete_story(self, project_id: int, story_id: int) -> None:
    #     """Delete a story identified by ID from the given project."""
    #     project = self._find_project(project_id)
    #     if project is None:
    #         raise ValueError("Project not found")

    #     stories = project.get("stories", [])
    #     new_stories = [s for s in stories if s.get("id") != story_id]
    #     if len(new_stories) == len(stories):
    #         raise ValueError("Story not found")

    #     project["stories"] = new_stories
    #     project["modified_at"] = _now_iso()
    #     self.save_data()
    #     print(f"Deleted story {story_id} from project {project_id}")

    # # ------------------ Task operations ------------------
    # def add_task_to_story(self, project_id: int, story_id: int, title: str, assigned_to: Optional[str] = None, estimated_hours: Optional[float] = None) -> Dict[str, Any]:
    #     """Add a task to the specified story. Tasks are simple dicts stored under 'tasks'."""
    #     title = (title or "").strip()
    #     if not title:
    #         raise ValueError("Task title cannot be blank")

    #     project = self._find_project(project_id)
    #     if project is None:
    #         raise ValueError("Project not found")

    #     for s in project.get("stories", []):
    #         if s.get("id") == story_id:
    #             # check duplicate task title
    #             for t in s.get("tasks", []):
    #                 if t.get("title", "").strip().lower() == title.lower():
    #                     raise ValueError("Task title already exists in story")

    #             task = Task(title=title, assigned_to=assigned_to, estimated_hours=estimated_hours).to_dict()
    #             s.setdefault("tasks", []).append(task)
    #             s["modified_at"] = _now_iso()
    #             # recalc progress
    #             s["progress"] = self._compute_progress(s)
    #             project["modified_at"] = _now_iso()
    #             self.save_data()
    #             print(f"Added task to story {story_id} in project {project_id}: {title}")
    #             return task

    #     raise ValueError("Story not found")

    # def mark_task_complete(self, project_id: int, story_id: int, task_title: str) -> Dict[str, Any]:
    #     """Mark a task as done by title and update story progress."""
    #     project = self._find_project(project_id)
    #     if project is None:
    #         raise ValueError("Project not found")

    #     for s in project.get("stories", []):
    #         if s.get("id") == story_id:
    #             for t in s.get("tasks", []):
    #                 if t.get("title", "").strip().lower() == (task_title or "").strip().lower():
    #                     t["status"] = "done"
    #                     s["modified_at"] = _now_iso()
    #                     s["progress"] = self._compute_progress(s)
    #                     project["modified_at"] = _now_iso()
    #                     self.save_data()
    #                     print(f"Task marked done: {task_title}")
    #                     return t

    #             raise ValueError("Task not found")

    #     raise ValueError("Story not found")

    # def _compute_progress(self, story: Dict[str, Any]) -> float:
    #     tasks = story.get("tasks", [])
    #     if not tasks:
    #         return 0.0
    #     done = sum(1 for t in tasks if t.get("status") == "done")
    #     return round((done / len(tasks)) * 100.0, 2)

    # # ------------------ Utility read access ------------------
    # def get_project(self, project_id: int) -> Dict[str, Any]:
    #     p = self._find_project(project_id)
    #     if p is None:
    #         raise ValueError("Project not found")
    #     return p

    # def get_story(self, project_id: int, story_id: int) -> Dict[str, Any]:
    #     p = self._find_project(project_id)
    #     if p is None:
    #         raise ValueError("Project not found")
    #     for s in p.get("stories", []):
    #         if s.get("id") == story_id:
    #             return s
    #     raise ValueError("Story not found")

    def create_project(self, title: str, description: str, owner: str) -> Dict[str, Any]:
        """Create a new project and persist it.

        Raises ValueError for blank titles or duplicate titles (case-insensitive).
        Returns the created project dict.
        """
        title = (title or "").strip()
        if not title:
            raise ValueError("Project title cannot be blank")

        # duplicate check
        for p in self._data.get("projects", []):
            if p.get("title", "").strip().lower() == title.lower():
                raise ValueError("Project title already exists")

        project = {
            "id": self._next_project_id(),
            "title": title,
            "description": description or "",
            "owner": owner or "",
            "stories": [],
            "created_at": _now_iso(),
            "modified_at": _now_iso(),
        }

        self._data.setdefault("projects", []).append(project)
        self.save_data()
        print(f"Project created: {project['id']} - {project['title']}")
        return project

    

__all__ = ["ProjectManager"]
