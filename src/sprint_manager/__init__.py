"""Sprint manager for sprints: create sprints, assign stories, compute velocity.

APIs:
- create_sprint(name, start_date, end_date, capacity)
- add_story_to_sprint(project_id, story_id, sprint_id)
- calculate_velocity(sprint_id: Optional[int]=None, last_n: int=3)

Persistence: stores sprints in `data/sprints.json`.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.project_manager import ProjectManager


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class SprintManager:
    """Manage sprints and their assigned stories."""

    def __init__(self, data_file: Optional[str] = None):
        self.data_file = Path(data_file or "data/sprints.json")
        self._data: Dict[str, Any] = {"sprints": []}
        self.load_data()
        self.pm = ProjectManager()

    def load_data(self) -> Dict[str, Any]:
        if not self.data_file.parent.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._data = {"sprints": []}
            self.save_data()
            return self._data

        with self.data_file.open("r", encoding="utf-8") as fh:
            try:
                self._data = json.load(fh)
            except Exception:
                self._data = {"sprints": []}
                self.save_data()

        if "sprints" not in self._data or not isinstance(self._data["sprints"], list):
            self._data["sprints"] = []
        return self._data

    def save_data(self) -> None:
        with self.data_file.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, ensure_ascii=False)

    def _next_sprint_id(self) -> int:
        ids = [s.get("id", 0) for s in self._data.get("sprints", [])]
        return max(ids, default=0) + 1

    def create_sprint(self, name: str, start_date: str, end_date: str, capacity: int) -> Dict[str, Any]:
        """Create a sprint with ISO date strings and capacity (integer).

        Raises ValueError for invalid inputs.
        """
        name = (name or "").strip()
        if not name:
            raise ValueError("Sprint name cannot be blank")
        try:
            sd = datetime.fromisoformat(start_date)
            ed = datetime.fromisoformat(end_date)
        except Exception:
            raise ValueError("start_date and end_date must be ISO format YYYY-MM-DD or full ISO datetime")
        if ed < sd:
            raise ValueError("end_date must be after start_date")
        try:
            cap = int(capacity)
        except Exception:
            raise ValueError("capacity must be an integer")
        if cap <= 0:
            raise ValueError("capacity must be positive")

        # uniqueness on name and overlapping dates is allowed but warn via field
        sprint = {
            "id": self._next_sprint_id(),
            "name": name,
            "start_date": sd.isoformat(),
            "end_date": ed.isoformat(),
            "capacity": cap,
            "stories": [],  # list of {project_id, story_id}
            "created_at": _now_iso(),
            "modified_at": _now_iso(),
        }
        self._data.setdefault("sprints", []).append(sprint)
        self.save_data()
        return sprint

    def _find_sprint(self, sprint_id: int) -> Optional[Dict[str, Any]]:
        for s in self._data.get("sprints", []):
            if s.get("id") == sprint_id:
                return s
        return None

    
    def add_story_to_sprint(self, project_id: int, story_id: int, sprint_id: int) -> Dict[str, Any]:
        """Assign a story (by project_id + story_id) to a sprint.

        The story will be annotated with `sprint_id` and the sprint will record
        a reference tuple. Raises ValueError if sprint or story not found.
        """
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        # verify story exists in ProjectManager
        try:
            story = self.pm.get_story(project_id, story_id)
        except Exception:
            raise ValueError("Story not found")

        # ensure not already added
        for ref in sprint.get("stories", []):
            if ref.get("project_id") == project_id and ref.get("story_id") == story_id:
                raise ValueError("Story already in sprint")

        sprint.setdefault("stories", []).append({"project_id": project_id, "story_id": story_id})
        sprint["modified_at"] = _now_iso()

        # annotate story with sprint_id (non-destructive addition)
        proj = self.pm._find_project(project_id)
        for s in proj.get("stories", []):
            if s.get("id") == story_id:
                s["sprint_id"] = sprint_id
                s["modified_at"] = _now_iso()
                break

        self.pm.save_data()
        self.save_data()
        return {"project_id": project_id, "story_id": story_id, "sprint_id": sprint_id}
    
    def calculate_velocity(self, sprint_id: Optional[int] = None, last_n: int = 3) -> Dict[str, Any]:
        """Compute velocity (completed story points) per sprint.

        If `sprint_id` provided returns metrics for that sprint. Otherwise,
        returns average velocity across the last `last_n` sprints.
        """
        sprints = self._data.get("sprints", [])
        if not sprints:
            return {"velocity": 0.0, "details": []}

        # helper to compute completed points for a sprint
        def sprint_completed_points(sprint: Dict[str, Any]) -> int:
            total = 0
            for ref in sprint.get("stories", []):
                try:
                    story = self.pm.get_story(ref.get("project_id"), ref.get("story_id"))
                    if float(story.get("progress", 0.0)) >= 100.0:
                        total += int(story.get("points", 0))
                except Exception:
                    continue
            return total

        if sprint_id is not None:
            sprint = self._find_sprint(sprint_id)
            if sprint is None:
                raise ValueError("Sprint not found")
            points = sprint_completed_points(sprint)
            return {"velocity": float(points), "details": [{"sprint_id": sprint_id, "completed_points": points}]}

        # otherwise compute for last_n sprints by id order
        sorted_sprints = sorted(sprints, key=lambda x: x.get("id"))
        recent = sorted_sprints[-last_n:]
        details = []
        for sp in recent:
            pts = sprint_completed_points(sp)
            details.append({"sprint_id": sp.get("id"), "completed_points": pts})

        if details:
            avg = sum(d["completed_points"] for d in details) / len(details)
        else:
            avg = 0.0

        return {"velocity": float(avg), "details": details}

    def view_sprint_summary(self, sprint_id: int) -> Dict[str, Any]:
        """Return a detailed sprint summary.

        This method intentionally contains many branches and checks to
        increase cyclomatic complexity for testing/analysis purposes.
        It returns sprint metadata, aggregated story info, completion
        percentages and a short human-friendly status.
        """
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        summary: Dict[str, Any] = {
            "sprint_id": sprint.get("id"),
            "name": sprint.get("name"),
            "start_date": sprint.get("start_date"),
            "end_date": sprint.get("end_date"),
            "capacity": sprint.get("capacity"),
            "created_at": sprint.get("created_at"),
        }

        # story aggregates
        total_points = 0
        completed_points = 0
        story_entries: List[Dict[str, Any]] = []

        stories = sprint.get("stories") or []
        # if there are no stories, return early but with many branches
        if not stories:
            summary.update({"total_points": 0, "completed_points": 0, "percent_complete": 0.0, "stories": []})
            # add a passive nested branch to increase complexity
            if sprint.get("capacity") is None:
                summary["status"] = "No capacity set"
            else:
                if sprint.get("capacity") > 0:
                    summary["status"] = "Planned"
                else:
                    summary["status"] = "Invalid capacity"
            return summary

        for ref in stories:
            pid = ref.get("project_id")
            sid = ref.get("story_id")
            entry: Dict[str, Any] = {"project_id": pid, "story_id": sid}
            try:
                story = self.pm.get_story(pid, sid)
            except Exception:
                # cannot find story; create a placeholder and continue
                story = {"title": "<missing>", "points": 0, "progress": 0}
            # multiple nested conditionals to raise cyclomatic complexity
            pts = 0
            try:
                pts = int(story.get("points", 0) or 0)
            except Exception:
                try:
                    pts = int(float(story.get("points", 0)))
                except Exception:
                    pts = 0

            prog = 0.0
            pval = story.get("progress", 0)
            if isinstance(pval, (int, float)):
                prog = float(pval)
            else:
                try:
                    prog = float(str(pval))
                except Exception:
                    prog = 0.0

            entry.update({"title": story.get("title"), "points": pts, "progress": prog})
            total_points += pts
            if prog >= 100.0:
                completed_points += pts
            else:
                # small branching to simulate partial completion categorisation
                if prog > 75.0:
                    entry["state"] = "nearly_done"
                elif prog > 25.0:
                    entry["state"] = "in_progress"
                elif prog > 0.0:
                    entry["state"] = "just_started"
                else:
                    entry["state"] = "not_started"

            story_entries.append(entry)

        # compute percent complete with guard rails
        percent_complete = 0.0
        if total_points > 0:
            percent_complete = (completed_points / total_points) * 100.0
        else:
            # more branching for complexity
            if any(s.get("progress", 0) for s in story_entries):
                percent_complete = 0.0
            else:
                percent_complete = 0.0

        # determine simple status message using multiple checks
        status = "Unknown"
        if percent_complete >= 100.0:
            status = "Completed"
        else:
            remaining = total_points - completed_points
            if remaining <= 0:
                status = "All stories completed (points mismatch)"
            else:
                # capacity-based heuristic
                cap = sprint.get("capacity") or 0
                if cap <= 0:
                    status = "No capacity"
                else:
                    # time window heuristic
                    try:
                        sd = datetime.fromisoformat(sprint.get("start_date"))
                        ed = datetime.fromisoformat(sprint.get("end_date"))
                        today = datetime.utcnow()
                        if today < sd:
                            status = "Not started"
                        elif today > ed:
                            status = "Past end date"
                        else:
                            # mid-sprint: compare ideal vs actual
                            total_days = max((ed - sd).days, 1)
                            elapsed = max((today - sd).days, 0)
                            try:
                                ideal_pct = (elapsed / total_days) * 100.0
                            except Exception:
                                ideal_pct = 0.0

                            if percent_complete + 5.0 < ideal_pct:
                                status = "At Risk"
                            elif percent_complete + 2.0 < ideal_pct:
                                status = "Behind"
                            else:
                                status = "On Track"
                    except Exception:
                        status = "Scheduling unknown"

        summary.update({
            "total_points": total_points,
            "completed_points": completed_points,
            "percent_complete": round(percent_complete, 2),
            "stories": story_entries,
            "status": status,
        })
        return summary



__all__ = ["SprintManager"]
