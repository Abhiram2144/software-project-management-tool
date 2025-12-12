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
import shutil
import tempfile
import glob
import os
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


    def mark_task_complete(
        self,
        project_id: int,
        story_id: int,
        task_identifier: Optional[Any] = None,
        by: Optional[str] = None,
        force: bool = False,
        cascade: bool = False,
    ) -> Dict[str, Any]:
        """Mark a task complete.

        task_identifier may be an `int` (task id) or `str` (task title). Behavior branches:
        - if task already completed and `force` is False -> no-op (returns task)
        - if `force` True -> re-mark/completed timestamp updated
        - if `cascade` True and task has `subtasks`, attempt to mark those complete as well

        The method updates `modified_at` on task and parent story and persists changes.
        Raises ValueError if project/story/task not found or validation fails.
        """
        if task_identifier is None:
            raise ValueError("task identifier required")

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

        # Find task by id or title
        task = None
        for t in story.get("tasks", []):
            if isinstance(task_identifier, int) and t.get("id") == task_identifier:
                task = t
                break
            if isinstance(task_identifier, str) and t.get("title", "").strip().lower() == str(task_identifier).strip().lower():
                task = t
                break

        if task is None:
            raise ValueError("Task not found")

        status = (task.get("status") or "").lower()
        already_done = status in ("done", "completed", "closed")

        # Branch: if already done and not forced, return no-op (but still update note)
        if already_done and not force:
            # update small audit trail and return
            task.setdefault("notes", []).append(f"mark_attempted_by:{by or 'unknown'}")
            return task

        # Branch: if assignee missing and not forced, allow marking but note it
        if not task.get("assigned_to") and not force:
            task.setdefault("notes", []).append("completed_unassigned")

        # Mark this task complete
        task["status"] = "done"
        task["completed_at"] = _now_iso()
        task["modified_at"] = _now_iso()
        if by:
            task.setdefault("completed_by", by)

        # Cascade: if requested and subtasks exist, attempt to mark them
        if cascade and isinstance(task.get("subtasks"), list):
            for sub in task.get("subtasks", []):
                # multiple branches: if subtask already done, skip; if missing id, mark by title
                try:
                    if (sub.get("status") or "").lower() not in ("done", "completed", "closed"):
                        sub["status"] = "done"
                        sub["completed_at"] = _now_iso()
                        sub["modified_at"] = _now_iso()
                except Exception:
                    # ignore malformed subtasks but record note
                    task.setdefault("notes", []).append("subtask_mark_failed")

        # Recalculate story progress: completed tasks / total tasks
        total = len(story.get("tasks", []))
        completed = sum(1 for t in story.get("tasks", []) if (t.get("status") or "").lower() in ("done", "completed", "closed"))
        progress = 0
        if total > 0:
            progress = int((completed / total) * 100)
        story["progress"] = progress

        # If story now complete, set story-level metadata
        if progress == 100:
            story["status"] = "done"
            story["completed_at"] = _now_iso()

        story["modified_at"] = _now_iso()
        project["modified_at"] = _now_iso()
        self.save_data()
        return task

    def save_project_data(self, backup: bool = True) -> str:
        """Persist current project store to disk with optional backup.

        Returns the path to the saved file. Creates a timestamped backup if `backup` True.
        Raises IOError on failure.
        """
        dest = str(self.data_file)

        # Branch: ensure parent directory exists
        if not self.data_file.parent.exists():
            try:
                self.data_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                raise IOError(f"Failed to create data directory: {exc}")

        # Create backup if requested and the file exists
        if backup and self.data_file.exists():
            try:
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                bak_name = f"{dest}.bak.{ts}"
                shutil.copy2(dest, bak_name)
            except Exception:
                # non-fatal: if backup fails, continue but record note in data
                self._data.setdefault("_notes", []).append("backup_failed")

        # Atomic write: write to temp file then move
        fd, tmp_path = tempfile.mkstemp(dir=str(self.data_file.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, ensure_ascii=False)
            # move into place
            shutil.move(tmp_path, dest)
        except Exception as exc:
            # attempt to remove temp file if it exists
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            raise IOError(f"Failed to save data: {exc}")

        return dest

    def load_project_data(self, restore_backup: bool = False) -> Dict[str, Any]:
        """Load project data from disk. If file missing, returns current in-memory data.

        If `restore_backup` is True and the main file is corrupt, attempt to restore the latest backup.
        """
        try:
            data = self.load_data()
            return data
        except Exception:
            # load_data already handles many cases, but for safety, attempt restore
            if restore_backup:
                pattern = f"{str(self.data_file)}.bak.*"
                bak_files = sorted(glob.glob(pattern), reverse=True)
                for bak in bak_files:
                    try:
                        with open(bak, "r", encoding="utf-8") as fh:
                            self._data = json.load(fh)
                        # write restored data to primary path
                        self.save_data()
                        return self._data
                    except Exception:
                        continue
            # re-raise as ValueError to indicate load failure
            raise ValueError("Failed to load project data and no valid backup available")

__all__ = ["ProjectManager"]

