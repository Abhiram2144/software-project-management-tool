"""
ProjectManager module for Sprint 1 user stories.

Provides project creation, listing and story addition with JSON persistence
under `data/projects.json`.
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
class Story:
    id: int
    title: str
    description: str
    points: int
    tasks: List[Dict[str, Any]]
    created_at: str
    modified_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProjectManager:
    """Manage projects and stories persisted as JSON.

    Methods are intentionally simple and deterministic for Sprint 1.
    """

    def __init__(self, data_file: Optional[str] = None):
        self.data_file = Path(data_file or "data/projects.json")
        self._data: Dict[str, Any] = {"projects": []}
        self.load_data()

    def load_data(self) -> Dict[str, Any]:
        """Load data from disk; create empty store if missing."""
        if not self.data_file.parent.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            self._data = {"projects": []}
            self.save_data()
            return self._data

        with self.data_file.open("r", encoding="utf-8") as fh:
            try:
                self._data = json.load(fh)
            except Exception:
                # If file is corrupt, reinitialize
                self._data = {"projects": []}
                self.save_data()

        if "projects" not in self._data or not isinstance(self._data["projects"], list):
            self._data["projects"] = []

        return self._data

    def save_data(self) -> None:
        """Persist current data to disk."""
        with self.data_file.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, ensure_ascii=False)

    def _next_project_id(self) -> int:
        ids = [p.get("id", 0) for p in self._data.get("projects", [])]
        return max(ids, default=0) + 1

    def create_project(self, title: str, description: str, owner: str) -> Dict[str, Any]:
        """Create a new project.

        Raises ValueError on blank title or duplicate title (case-insensitive).
        Returns the project dict.
        """
        title = (title or "").strip()
        if not title:
            raise ValueError("Project title cannot be blank")

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
        return project

    def list_projects(self) -> List[Dict[str, Any]]:
        """Return a summary list of projects (id, title, owner, story_count)."""
        out: List[Dict[str, Any]] = []
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

    def _next_story_id(self, project: Dict[str, Any]) -> int:
        ids = [s.get("id", 0) for s in project.get("stories", [])]
        return max(ids, default=0) + 1

    def add_story_to_project(self, project_id: int, title: str, description: str, points: int) -> Dict[str, Any]:
        """Add a user story under the given project.

        Raises ValueError for blank title, duplicate titles within a project, or
        if the project does not exist. Returns the created story dict.
        """
        title = (title or "").strip()
        if not title:
            raise ValueError("Story title cannot be blank")

        project = self._find_project(project_id)
        if project is None:
            raise ValueError("Project not found")

        for s in project.get("stories", []):
            if s.get("title", "").strip().lower() == title.lower():
                raise ValueError("Story title already exists in project")

        story = Story(
            id=self._next_story_id(project),
            title=title,
            description=description or "",
            points=int(points or 0),
            tasks=[],
            created_at=_now_iso(),
            modified_at=_now_iso(),
        ).to_dict()

        project.setdefault("stories", []).append(story)
        project["modified_at"] = _now_iso()
        self.save_data()
        return story


__all__ = ["ProjectManager"]
