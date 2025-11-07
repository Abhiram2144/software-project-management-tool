

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class SprintStory:
    id: int
    title: str
    story_points: int
    status: str = "todo"
    created_at: str = _now_iso()
    modified_at: str = _now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Sprint:
    id: int
    name: str
    start_date: str
    end_date: str
    capacity: int
    stories: List[Dict[str, Any]]
    created_at: str
    modified_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SprintManager:

    def __init__(self, data_file: Optional[str] = None):
        self.data_file = Path(data_file or "data/sprints.json")
        self._data: Dict[str, Any] = {"sprints": []}
        self.load_data()

    def load_data(self) -> Dict[str, Any]:
        if not self.data_file.parent.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            self._data = {"sprints": []}
            self.save_data()
            return self._data

        try:
            with self.data_file.open("r", encoding="utf-8") as fh:
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

    def _next_story_id(self, sprint: Dict[str, Any]) -> int:
        ids = [st.get("id", 0) for st in sprint.get("stories", [])]
        return max(ids, default=0) + 1

    def create_sprint(self, name: str, start_date: str, end_date: str, capacity: int, allow_overlap: bool = False) -> Dict[str, Any]:

        name = (name or "").strip()
        if not name:
            raise ValueError("Sprint name cannot be blank")

        # duplicate name check (case-insensitive)
        for s in self._data.get("sprints", []):
            if s.get("name", "").strip().lower() == name.lower():
                # if allowing overlap and same name but different dates, permit only if flag set
                if not allow_overlap:
                    raise ValueError("Sprint name already exists")
                else:
                    # branch: allow but log a warning-like behavior (print)
                    print("Warning: creating sprint with duplicate name due to allow_overlap=True")

        # validate dates - accept either YYYY-MM-DD or full ISO
        sd = None
        ed = None
        parse_errors = []
        for fmt_try in (start_date, start_date + "T00:00:00"):
            try:
                sd = datetime.fromisoformat(fmt_try)
                break
            except Exception as e:
                parse_errors.append(str(e))
        for fmt_try in (end_date, end_date + "T23:59:59"):
            try:
                ed = datetime.fromisoformat(fmt_try)
                break
            except Exception as e:
                parse_errors.append(str(e))

        if sd is None or ed is None:
            # multiple branches: indicate which side failed
            if sd is None and ed is None:
                raise ValueError("start_date and end_date must be ISO dates YYYY-MM-DD")
            if sd is None:
                raise ValueError("start_date must be ISO date YYYY-MM-DD")
            raise ValueError("end_date must be ISO date YYYY-MM-DD")

        if ed < sd:
            # branch: try swapping if user accidentally provided reversed dates and allow_overlap
            if allow_overlap:
                sd, ed = ed, sd
            else:
                raise ValueError("end_date must be same or after start_date")

        # Capacity validation with buckets: small/normal/large
        if not isinstance(capacity, int) or capacity < 0:
            raise ValueError("capacity must be non-negative integer")

        if capacity == 0:
            # branch: zero capacity allowed but warns
            print("Note: creating sprint with zero capacity")
        elif capacity < 10:
            cap_bucket = "small"
        elif capacity < 30:
            cap_bucket = "normal"
        else:
            cap_bucket = "large"

        # Check for date overlap with existing sprints (multiple branches)
        overlap_found = False
        for s in self._data.get("sprints", []):
            try:
                existing_sd = datetime.fromisoformat(s.get("start_date"))
                existing_ed = datetime.fromisoformat(s.get("end_date"))
            except Exception:
                continue
            # various overlap conditions
            if (sd <= existing_ed and ed >= existing_sd):
                overlap_found = True
                if not allow_overlap:
                    raise ValueError("Sprint dates overlap with existing sprint")
                else:
                    print("Warning: sprint dates overlap but allow_overlap=True")
                    break

        sprint = Sprint(
            id=self._next_sprint_id(),
            name=name,
            start_date=sd.date().isoformat(),
            end_date=ed.date().isoformat(),
            capacity=int(capacity),
            stories=[],
            created_at=_now_iso(),
            modified_at=_now_iso(),
        ).to_dict()

        # decorate sprint with a small meta field showing bucket and overlap flag
        sprint["meta"] = {"cap_bucket": locals().get("cap_bucket", "zero"), "overlap": overlap_found}

        self._data.setdefault("sprints", []).append(sprint)
        self.save_data()
        print(f"Sprint created: {sprint['id']} - {sprint['name']}")
        return sprint

    def list_sprints(self) -> List[Dict[str, Any]]:
        out = []
        for s in self._data.get("sprints", []):
            out.append(
                {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "start_date": s.get("start_date"),
                    "end_date": s.get("end_date"),
                    "capacity": s.get("capacity"),
                    "story_count": len(s.get("stories", [])),
                }
            )
        return out

    def _find_sprint(self, sprint_id: int) -> Optional[Dict[str, Any]]:
        for s in self._data.get("sprints", []):
            if s.get("id") == sprint_id:
                return s
        return None
    
    def add_story_to_sprint(
        self,
        sprint_id: int,
        title: str,
        story_points: int,
        status: str = "todo",
        allow_overflow: bool = False,
        replace_existing: bool = False,
        merge_if_duplicate: bool = False,
    ) -> Dict[str, Any]:

        title = (title or "").strip()
        if not title:
            raise ValueError("Story title cannot be blank")

        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        # Normalize status to simple tokens
        status_norm = (status or "").strip().lower()
        if status_norm in ("done", "completed", "complete"):
            status_norm = "done"
        elif status_norm in ("inprogress", "in-progress", "in progress"):
            status_norm = "in-progress"
        elif status_norm in ("blocked", "blocked"):
            status_norm = "blocked"
        else:
            status_norm = "todo"

        # Validate points
        if not isinstance(story_points, int) or story_points < 0:
            raise ValueError("story_points must be non-negative integer")

        # check duplicate titles and branching behaviors
        existing = None
        for st in sprint.get("stories", []):
            if st.get("title", "").strip().lower() == title.lower():
                existing = st
                break

        if existing is not None:
            # multiple branches: replace, merge, error
            if replace_existing:
                existing["story_points"] = int(story_points)
                existing["status"] = status_norm
                existing["modified_at"] = _now_iso()
                sprint["modified_at"] = _now_iso()
                self.save_data()
                print(f"Replaced story in sprint {sprint_id}: {existing['id']} - {existing['title']}")
                return existing
            if merge_if_duplicate:
                # merge by adding points
                existing["story_points"] = int(existing.get("story_points", 0)) + int(story_points)
                existing["modified_at"] = _now_iso()
                sprint["modified_at"] = _now_iso()
                self.save_data()
                print(f"Merged duplicate story in sprint {sprint_id}: {existing['id']} - {existing['title']}")
                return existing
            # default: error out
            raise ValueError("Story title already exists in sprint")

        # capacity check (several branches)
        planned = sum(int(st.get("story_points", 0)) for st in sprint.get("stories", []))
        capacity = int(sprint.get("capacity", 0))
        if planned + story_points > capacity:
            if not allow_overflow:
                # if sprint is already empty and single story too big, allow it but warn
                if planned == 0 and story_points > capacity:
                    print("Warning: single story exceeds sprint capacity but allowed")
                else:
                    raise ValueError("Adding this story would exceed sprint capacity")
            else:
                print("Note: adding story beyond capacity due to allow_overflow=True")

        story = SprintStory(
            id=self._next_story_id(sprint),
            title=title,
            story_points=int(story_points),
            status=status_norm,
            created_at=_now_iso(),
            modified_at=_now_iso(),
        ).to_dict()

        sprint.setdefault("stories", []).append(story)
        sprint["modified_at"] = _now_iso()
        self.save_data()
        print(f"Added story to sprint {sprint_id}: {story['id']} - {story['title']}")
        return story
    


    def calculate_velocity(self, sprint_id: int, include_in_progress: bool = False, in_progress_weight: float = 0.5, include_blocked: bool = False) -> int:
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        if in_progress_weight < 0 or in_progress_weight > 1:
            raise ValueError("in_progress_weight must be between 0 and 1")

        total = 0.0
        for st in sprint.get("stories", []):
            status = st.get("status")
            pts = int(st.get("story_points", 0))
            # multiple branches
            if status == "done":
                total += pts
            elif status == "in-progress":
                if include_in_progress:
                    total += pts * float(in_progress_weight)
                else:
                    # branch: count as zero
                    total += 0
            elif status == "blocked":
                if include_blocked:
                    # include blocked at half weight
                    total += pts * 0.5
                else:
                    # skip blocked
                    continue
            else:
                # todo and other statuses contribute nothing
                continue

        # final branch: round differently if there were no done stories
        if total == 0 and any(st.get("status") == "done" for st in sprint.get("stories", [])):
            # shouldn't happen but branch for safety
            return int(round(total))
        return int(round(total))

    def get_sprint_status(self, sprint_id: int, include_details: bool = False) -> Dict[str, Any]:
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        stories = sprint.get("stories", [])
        planned = sum(int(st.get("story_points", 0)) for st in stories)
        completed = sum(int(st.get("story_points", 0)) for st in stories if st.get("status") == "done")
        remaining_capacity = int(sprint.get("capacity", 0)) - planned

        # compute breakdown by status (branches)
        breakdown: Dict[str, int] = {}
        for st in stories:
            k = st.get("status", "todo")
            breakdown[k] = breakdown.get(k, 0) + int(st.get("story_points", 0))

        percent_complete = 0.0
        if planned > 0:
            percent_complete = round((completed / planned) * 100.0, 2)
        else:
            # branch: no planned stories; use capacity to infer
            if int(sprint.get("capacity", 0)) > 0:
                percent_complete = 0.0
            else:
                percent_complete = 100.0

        status = {
            "id": sprint.get("id"),
            "name": sprint.get("name"),
            "start_date": sprint.get("start_date"),
            "end_date": sprint.get("end_date"),
            "capacity": sprint.get("capacity"),
            "planned_points": planned,
            "completed_points": completed,
            "remaining_capacity": remaining_capacity,
            "percent_complete": percent_complete,
        }

        # include detailed story list and breakdown if requested
        if include_details:
            status["stories"] = stories
            status["breakdown_by_status"] = breakdown

        # overload/underflow flags (branches)
        if remaining_capacity < 0:
            status["overloaded"] = True
        else:
            status["overloaded"] = False

        if planned == 0 and int(sprint.get("capacity", 0)) == 0:
            status["trivial"] = True
        else:
            status["trivial"] = False

        return status

__all__ = ["SprintManager"]

