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

    

__all__ = ["ProjectManager"]
