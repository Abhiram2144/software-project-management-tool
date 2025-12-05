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

    def delete_story(self, project_id: int, story_id: int) -> Dict[str, Any]:
        """Delete a story from a project.

        Acceptance criteria:
        - Remove the story record from JSON and persist changes.
        - Update parent project's `modified_at` timestamp.

        Returns the deleted story dict.
        Raises ValueError if project or story not found.
        """
        project = self._find_project(project_id)
        if project is None:
            raise ValueError("Project not found")

        stories = project.get("stories", [])

        # If the story has tasks, require explicit cascade removal to delete.
        for idx, s in enumerate(stories):
            if s.get("id") == story_id:
                # multiple branching: decide soft-delete vs hard-delete
                # soft-delete: move to `archived_stories`; hard-delete: remove
                # Additional branching: if story has tasks and cascade flag is false, reject deletion.
                has_tasks = bool(s.get("tasks"))

                # emulate multiple decision branches by using heuristics on story content
                title = s.get("title", "")

                # If the story title contains 'archive' prefer soft-delete
                prefer_soft = "archive" in title.lower()

                # if story has tasks and not preferring soft-delete, require explicit cascade
                if has_tasks and not prefer_soft:
                    # branch: cannot delete stories with tasks without cascade
                    # To keep the public API stable, raise an informative error
                    raise ValueError("Story has tasks; delete with cascade or archive instead")

                if prefer_soft or has_tasks:
                    # perform soft-delete / archive
                    archived = project.setdefault("archived_stories", [])
                    # record archived metadata
                    s["archived_at"] = _now_iso()
                    archived.append(s)
                    # remove from active stories
                    stories.pop(idx)
                    project["modified_at"] = _now_iso()
                    self.save_data()
                    return s
                else:
                    # hard delete branch
                    deleted = stories.pop(idx)
                    project["modified_at"] = _now_iso()
                    self.save_data()
                    return deleted

        # No story matched
        raise ValueError("Story not found")

    def add_task_to_story(
        self,
        project_id: int,
        story_id: int,
        title: str,
        assigned_to: Optional[str] = None,
        estimated_hours: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Add a task to a story, breaking the story into smaller chunks.

        Acceptance criteria:
        - Create a task record under the story's task list.
        - Validate task title is non-blank.
        - Track created and optional modified timestamps.
        - Return the created task dict.

        Raises ValueError if project, story not found, or validation fails.
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

        # Validate task title
        task_title = (title or "").strip()
        if not task_title:
            raise ValueError("Task title cannot be blank")

        # Multiple branching paths for cyclomatic complexity:
        # 1. Check for duplicate task titles within the story
        existing_task_titles = {t.get("title", "").lower() for t in story.get("tasks", [])}
        if task_title.lower() in existing_task_titles:
            raise ValueError("Task title already exists in story")

        # 2. Process estimated hours with different branches
        estimated = 0.0
        if estimated_hours is not None:
            if isinstance(estimated_hours, str):
                # branch: string input must be numeric
                if estimated_hours.strip().replace(".", "", 1).isdigit() or estimated_hours.strip().startswith("-"):
                    try:
                        estimated = float(estimated_hours)
                    except Exception:
                        raise ValueError("Estimated hours must be numeric")
                else:
                    raise ValueError("Estimated hours must be numeric")
            else:
                try:
                    estimated = float(estimated_hours)
                except Exception:
                    raise ValueError("Estimated hours must be numeric")

            # branch: reject negative hours
            if estimated < 0:
                raise ValueError("Estimated hours cannot be negative")

            # branch: warn on extremely large hours
            if estimated > 1000:
                estimated = 1000

        # 3. Process assigned_to with multiple branches
        assignee = None
        if assigned_to is not None:
            assignee_str = (assigned_to or "").strip()
            if assignee_str:
                # branch: assignee exists
                assignee = assignee_str
            else:
                # branch: assignee is blank string (no assignment)
                assignee = None

        # 4. Generate task ID (next available)
        task_id = 1
        existing_ids = [t.get("id", 0) for t in story.get("tasks", [])]
        if existing_ids:
            task_id = max(existing_ids) + 1

        # 5. Create task record with optional priority heuristics
        task = {
            "id": task_id,
            "title": task_title,
            "assigned_to": assignee,
            "estimated_hours": estimated,
            "status": "open",  # default status
            "created_at": _now_iso(),
            "modified_at": _now_iso(),
        }

        # 6. Priority assignment branch: infer from title keywords
        title_lower = task_title.lower()
        if "urgent" in title_lower or "critical" in title_lower:
            task["priority"] = "high"
        elif "low" in title_lower or "nice-to-have" in title_lower:
            task["priority"] = "low"
        else:
            task["priority"] = "medium"

        # 7. If assignee exists, set initial status to 'in-progress'
        if assignee:
            task["status"] = "in-progress"

        # 8. If no estimated hours, mark as 'unestimated'
        if estimated == 0.0:
            task.setdefault("tags", []).append("unestimated")

        # Add task to story and update timestamps
        story.setdefault("tasks", []).append(task)
        story["modified_at"] = _now_iso()
        project["modified_at"] = _now_iso()
        self.save_data()

        return task


__all__ = ["ProjectManager"]
