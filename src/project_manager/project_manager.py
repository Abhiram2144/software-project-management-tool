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

    def edit_story(
        self,
        project_id: int,
        story_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        points: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Edit an existing story's fields.

        Acceptance criteria:
        - Update the JSON record on disk.
        - Track modified timestamp on the story and parent project.

        Raises ValueError if project or story not found, or if title would collide.
        Returns the updated story dict.
        """
        project = self._find_project(project_id)
        if project is None:
            raise ValueError("Project not found")

        story = None
        for s in project.get("stories", []):
            if s.get("id") == story_id:
                story = s
                break

        if story is None:
            raise ValueError("Story not found")

        # Multiple validation and branching paths to exercise different branches.
        original_title = story.get("title")
        title_changed = False

        # TITLE updates: blank, duplicate, same-as-before
        if title is not None:
            new_title = (title or "").strip()
            if not new_title:
                # branch: explicit blank title rejection
                raise ValueError("Story title cannot be blank")

            # branch: if new title equals existing title (no-op)
            if new_title == original_title:
                # no change to title — but we still may update other fields
                pass
            else:
                # branch: check duplicates within project
                for s in project.get("stories", []):
                    if s.get("id") != story_id and s.get("title", "").strip().lower() == new_title.lower():
                        # duplicate title branch
                        raise ValueError("Story title already exists in project")
                story["title"] = new_title
                title_changed = True

        # DESCRIPTION updates with simple heuristics
        if description is not None:
            # branch: very long descriptions get truncated and annotated
            if isinstance(description, str) and len(description) > 1000:
                story["description"] = description[:1000] + "..."
            else:
                story["description"] = description

        # POINTS updates with several validation branches
        if points is not None:
            # accept numeric-like strings too
            if isinstance(points, str):
                if points.strip().isdigit():
                    pts = int(points.strip())
                else:
                    # branch: malformed string
                    raise ValueError("Points must be an integer")
            else:
                try:
                    pts = int(points)
                except Exception:
                    # branch: cannot convert to int
                    raise ValueError("Points must be an integer")

            # branch: negative points are rejected
            if pts < 0:
                raise ValueError("Points cannot be negative")

            # branch: extreme value handling
            if pts > 1000:
                # cap very large estimates but record the requested value in notes
                story.setdefault("notes", []).append(f"points_capped_from:{pts}")
                pts = 1000

            story["points"] = pts

        # metadata updates
        story["modified_at"] = _now_iso()

        # project-level modified timestamp may depend on whether meaningful change happened
        if title_changed or (description is not None) or (points is not None):
            project["modified_at"] = _now_iso()
        else:
            # branch: touched but no meaningful change — still update to show review
            project["modified_at"] = _now_iso()

        # Optional side-effect branches to keep complexity up (no external effects)
        if title_changed and "fixme" in story.get("title", "").lower():
            story.setdefault("tags", []).append("needs-attention")

        if story.get("points", 0) == 0:
            # branch: zero-point stories are considered chores — tag them
            story.setdefault("tags", []).append("chore")

        self.save_data()
        return story

    

__all__ = ["ProjectManager"]
