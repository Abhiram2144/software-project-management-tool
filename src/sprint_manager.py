"""
sprint_manager.py
Manages sprint creation, tracking, and velocity calculations.
Handles sprint planning, start and end dates, and story assignments.
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

    def create_sprint(self, name: str, start_date: str, end_date: str, capacity: int) -> Dict[str, Any]:
        name = (name or "").strip()
        if not name:
            raise ValueError("Sprint name cannot be blank")

        # duplicate name check (case-insensitive)
        for s in self._data.get("sprints", []):
            if s.get("name", "").strip().lower() == name.lower():
                raise ValueError("Sprint name already exists")

        # validate dates
        try:
            sd = datetime.fromisoformat(start_date)
            ed = datetime.fromisoformat(end_date)
        except Exception:
            raise ValueError("start_date and end_date must be ISO dates YYYY-MM-DD")
        if ed < sd:
            raise ValueError("end_date must be same or after start_date")

        if not isinstance(capacity, int) or capacity < 0:
            raise ValueError("capacity must be non-negative integer")

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
    
    def add_story_to_sprint(self, sprint_id: int, title: str, story_points: int, status: str = "todo") -> Dict[str, Any]:
       
        title = (title or "").strip()
        if not title:
            raise ValueError("Story title cannot be blank")

        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        for st in sprint.get("stories", []):
            if st.get("title", "").strip().lower() == title.lower():
                raise ValueError("Story title already exists in sprint")

        if not isinstance(story_points, int) or story_points < 0:
            raise ValueError("story_points must be non-negative integer")

        story = SprintStory(
            id=self._next_story_id(sprint),
            title=title,
            story_points=int(story_points),
            status=status,
            created_at=_now_iso(),
            modified_at=_now_iso(),
        ).to_dict()

        sprint.setdefault("stories", []).append(story)
        sprint["modified_at"] = _now_iso()
        self.save_data()
        print(f"Added story to sprint {sprint_id}: {story['id']} - {story['title']}")
        return story
    


    def calculate_velocity(self, sprint_id: int) -> int:
        """Calculate velocity as sum of story_points for stories with status == 'done'."""
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        total = 0
        for st in sprint.get("stories", []):
            if st.get("status") == "done":
                total += int(st.get("story_points", 0))
        return total

    def get_sprint_status(self, sprint_id: int) -> Dict[str, Any]:
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        planned = sum(int(st.get("story_points", 0)) for st in sprint.get("stories", []))
        completed = sum(int(st.get("story_points", 0)) for st in sprint.get("stories", []) if st.get("status") == "done")
        remaining_capacity = int(sprint.get("capacity", 0)) - planned
        return {
            "id": sprint.get("id"),
            "name": sprint.get("name"),
            "start_date": sprint.get("start_date"),
            "end_date": sprint.get("end_date"),
            "capacity": sprint.get("capacity"),
            "planned_points": planned,
            "completed_points": completed,
            "remaining_capacity": remaining_capacity,
            "stories": sprint.get("stories", []),
        }

__all__ = ["SprintManager"]

