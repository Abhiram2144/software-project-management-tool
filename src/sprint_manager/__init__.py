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

from src.project_manager.project_manager import ProjectManager


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class SprintManager:
    """Manage sprints and their assigned stories."""

    def __init__(self, data_file: Optional[str] = None, project_manager: Optional[ProjectManager] = None):
        self.data_file = Path(data_file or "data/sprints.json")
        self._data: Dict[str, Any] = {"sprints": []}
        self.load_data()
        # allow injecting a ProjectManager (useful for tests); otherwise create default
        if project_manager is not None:
            self.pm = project_manager
        else:
            # try to infer projects file in same directory as sprints file (helps tests using tmp_path)
            try:
                inferred = str(self.data_file.parent / "projects.json")
                self.pm = ProjectManager(data_file=inferred)
            except Exception:
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

    def _get_story(self, project_id: int, story_id: int) -> Dict[str, Any]:
        # ensure the ProjectManager has the latest on-disk state
        try:
            self.pm.load_data()
        except Exception:
            pass

        proj = self.pm._find_project(project_id)
        if proj is None:
            raise ValueError("Project not found")
        for s in proj.get("stories", []):
            if s.get("id") == story_id:
                return s
        raise ValueError("Story not found")

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
            story = self._get_story(project_id, story_id)
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
                    story = self._get_story(ref.get("project_id"), ref.get("story_id"))
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
                story = self._get_story(pid, sid)
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

    def generate_burndown_chart(self, sprint_id: int) -> Dict[str, Any]:
        """Generate a burndown dataset for the sprint.

        Returns a dict with `dates`, `ideal_remaining`, and `actual_remaining` lists.
        The implementation uses many control-flow branches to raise cyclomatic
        complexity while providing a plausible burndown estimation based on
        available story `points` and `progress` fields.
        """
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        # parse dates with defensive checks
        try:
            sd = datetime.fromisoformat(sprint.get("start_date"))
        except Exception:
            sd = datetime.utcnow()
        try:
            ed = datetime.fromisoformat(sprint.get("end_date"))
        except Exception:
            ed = sd

        # ensure at least 1 day span
        days = max((ed - sd).days, 0)
        if days <= 0:
            # single day sprint: create two points
            days = 1

        total_points = 0
        completed_points = 0
        stories = sprint.get("stories") or []
        # collect per-story snapshots (naive: only current progress available)
        snapshots: List[Dict[str, Any]] = []
        for ref in stories:
            pid = ref.get("project_id")
            sid = ref.get("story_id")
            try:
                story = self._get_story(pid, sid)
            except Exception:
                story = {"points": 0, "progress": 0}
            pts = 0
            try:
                pts = int(story.get("points", 0) or 0)
            except Exception:
                try:
                    pts = int(float(story.get("points", 0)))
                except Exception:
                    pts = 0
            prog = 0.0
            try:
                prog = float(story.get("progress", 0) or 0.0)
            except Exception:
                prog = 0.0

            total_points += pts
            if prog >= 100.0:
                completed_points += pts

            snapshots.append({"points": pts, "progress": prog})

        # build date list inclusive of start and end
        dates: List[str] = []
        for i in range(days + 1):
            try:
                d = sd + (ed - sd) * (i / max(days, 1))
            except Exception:
                d = sd
            dates.append(d.date().isoformat())

        # ideal remaining: linear decrement
        ideal_remaining: List[float] = []
        for i in range(len(dates)):
            try:
                ideal = max(total_points - (total_points * (i / max(len(dates) - 1, 1))), 0.0)
            except Exception:
                ideal = float(total_points)
            ideal_remaining.append(round(float(ideal), 2))

        # actual remaining: we only have current progress, so we spread completed
        # points across the elapsed days proportionally; this creates branches
        actual_remaining: List[float] = []
        # compute completed fraction
        if total_points <= 0:
            # nothing planned
            actual_remaining = [0.0 for _ in dates]
        else:
            frac_completed = float(completed_points) / float(total_points)
            # distribute completion across days with some heuristic
            for idx in range(len(dates)):
                # multiple nested conditions to increase complexity
                if idx == 0:
                    rem = float(total_points)
                else:
                    # an artificial piecewise model: early, mid, late
                    pct = idx / max(len(dates) - 1, 1)
                    if pct < 0.25:
                        applied = frac_completed * 0.2
                    elif pct < 0.5:
                        applied = frac_completed * 0.35
                    elif pct < 0.75:
                        applied = frac_completed * 0.25
                    else:
                        applied = frac_completed * 0.2

                    # bound applied between 0 and frac_completed
                    try:
                        applied = max(min(applied, frac_completed), 0.0)
                    except Exception:
                        applied = 0.0

                    rem = max(total_points * (1.0 - applied), 0.0)

                actual_remaining.append(round(float(rem), 2))

        # final packaging with a few additional derived fields
        result = {
            "sprint_id": sprint.get("id"),
            "dates": dates,
            "ideal_remaining": ideal_remaining,
            "actual_remaining": actual_remaining,
            "total_points": total_points,
            "completed_points": completed_points,
        }
        return result

    def track_sprint_retrospective(self, sprint_id: int, went_well: List[str], 
                                   went_poorly: List[str], improvements: List[str]) -> Dict[str, Any]:
        """Log retrospective feedback for a completed sprint.

        Tracks what went well, what went poorly, and actionable improvements.
        This method uses many branches and nested conditionals to increase
        cyclomatic complexity while validating and organizing retrospective data.
        """
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        # defensive list initialization
        well_items = []
        if went_well is not None:
            try:
                if isinstance(went_well, list):
                    well_items = went_well
                else:
                    well_items = [str(went_well)]
            except Exception:
                well_items = []
        else:
            well_items = []

        poor_items = []
        if went_poorly is not None:
            try:
                if isinstance(went_poorly, list):
                    poor_items = went_poorly
                else:
                    poor_items = [str(went_poorly)]
            except Exception:
                poor_items = []
        else:
            poor_items = []

        improve_items = []
        if improvements is not None:
            try:
                if isinstance(improvements, list):
                    improve_items = improvements
                else:
                    improve_items = [str(improvements)]
            except Exception:
                improve_items = []
        else:
            improve_items = []

        # filter empty/whitespace entries with multiple branches
        cleaned_well: List[str] = []
        for item in well_items:
            try:
                cleaned = str(item).strip()
                if cleaned:
                    cleaned_well.append(cleaned)
                else:
                    # track empty items separately
                    pass
            except Exception:
                pass

        cleaned_poor: List[str] = []
        for item in poor_items:
            try:
                cleaned = str(item).strip()
                if cleaned:
                    cleaned_poor.append(cleaned)
                else:
                    pass
            except Exception:
                pass

        cleaned_improve: List[str] = []
        for item in improve_items:
            try:
                cleaned = str(item).strip()
                if cleaned:
                    cleaned_improve.append(cleaned)
                else:
                    pass
            except Exception:
                pass

        # categorize sentiment and priority
        sentiment = "neutral"
        if cleaned_well and cleaned_poor:
            # both positive and negative feedback
            well_count = len(cleaned_well)
            poor_count = len(cleaned_poor)
            if well_count > poor_count:
                sentiment = "positive"
            elif poor_count > well_count:
                sentiment = "negative"
            else:
                sentiment = "mixed"
        else:
            # edge cases
            if cleaned_well and not cleaned_poor:
                sentiment = "very_positive"
            elif cleaned_poor and not cleaned_well:
                sentiment = "very_negative"
            else:
                # both empty
                sentiment = "no_feedback"

        # compute improvement priority
        priority = "low"
        if cleaned_improve:
            imp_count = len(cleaned_improve)
            if imp_count >= 5:
                priority = "critical"
            elif imp_count >= 3:
                priority = "high"
            elif imp_count >= 1:
                priority = "medium"
            else:
                priority = "low"
        else:
            # no improvements provided
            if cleaned_poor:
                # but there were problems
                priority = "needs_planning"
            else:
                priority = "none"

        # validate sprint completion state
        sprint_status = "unknown"
        try:
            sd = datetime.fromisoformat(sprint.get("start_date"))
            ed = datetime.fromisoformat(sprint.get("end_date"))
            today = datetime.utcnow()
            if today < sd:
                sprint_status = "not_started"
            elif today > ed:
                sprint_status = "completed"
            else:
                sprint_status = "in_progress"
        except Exception:
            sprint_status = "invalid_dates"

        # compute team health based on feedback balance
        team_health = 50  # neutral baseline
        if cleaned_well:
            team_health += min(len(cleaned_well) * 10, 25)
        if cleaned_poor:
            team_health -= min(len(cleaned_poor) * 8, 25)
        if cleaned_improve:
            team_health += min(len(cleaned_improve) * 5, 15)
        
        # clamp health between 0 and 100
        try:
            team_health = max(0, min(team_health, 100))
        except Exception:
            team_health = 50

        # build retrospective record
        retrospective = {
            "sprint_id": sprint_id,
            "went_well": cleaned_well,
            "went_poorly": cleaned_poor,
            "improvements": cleaned_improve,
            "sentiment": sentiment,
            "priority": priority,
            "sprint_status": sprint_status,
            "team_health": team_health,
            "logged_at": _now_iso(),
        }

        # store retrospective in sprint data
        if "retrospectives" not in sprint:
            sprint["retrospectives"] = []
        
        # check for duplicates or overwrites
        existing_retros = sprint.get("retrospectives", [])
        if existing_retros:
            # if overwriting, mark as superseded
            for retro in existing_retros:
                try:
                    retro["superseded"] = True
                except Exception:
                    pass

        sprint["retrospectives"].append(retrospective)
        sprint["modified_at"] = _now_iso()

        # compute aggregate metrics across all retrospectives
        all_retros = sprint.get("retrospectives", [])
        total_feedback_items = 0
        total_well = 0
        total_poor = 0
        total_improve = 0
        health_scores = []

        for retro in all_retros:
            try:
                if not retro.get("superseded", False):
                    total_well += len(retro.get("went_well", []))
                    total_poor += len(retro.get("went_poorly", []))
                    total_improve += len(retro.get("improvements", []))
                    h = retro.get("team_health", 50)
                    if isinstance(h, (int, float)):
                        health_scores.append(float(h))
            except Exception:
                pass

        total_feedback_items = total_well + total_poor + total_improve

        # compute average health
        avg_health = 50.0
        if health_scores:
            try:
                avg_health = sum(health_scores) / len(health_scores)
            except Exception:
                avg_health = 50.0

        # save to persistent storage
        self.save_data()

        # return comprehensive retrospective result
        return {
            "sprint_id": sprint_id,
            "retrospective": retrospective,
            "aggregate_metrics": {
                "total_well_items": total_well,
                "total_poorly_items": total_poor,
                "total_improvement_items": total_improve,
                "total_feedback_items": total_feedback_items,
                "average_team_health": round(avg_health, 2),
            },
            "message": f"Retrospective logged for sprint {sprint_id}",
        }

    def _velocity_log_path(self) -> Path:
        return Path("data/velocity_log.json")

    def _load_velocity_log(self) -> List[Dict[str, Any]]:
        p = self._velocity_log_path()
        if not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            return []
        try:
            with p.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return []

    def _append_velocity_log(self, record: Dict[str, Any]) -> None:
        logs = self._load_velocity_log()
        logs.append(record)
        p = self._velocity_log_path()
        with p.open("w", encoding="utf-8") as fh:
            json.dump(logs, fh, indent=2, ensure_ascii=False)

    def set_sprint_status(self, sprint_id: int, status: str) -> Dict[str, Any]:
        """Set the sprint `status`. If set to Completed, recalculate velocity

        and append an entry to `data/velocity_log.json`. Returns a dict with
        message and computed velocities.
        """
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        sprint["status"] = status
        sprint["modified_at"] = _now_iso()
        self.save_data()

        # when completed, compute velocities and persist log
        if isinstance(status, str) and status.strip().lower() == "completed":
            # sprint-specific completed points
            try:
                sprint_vel = float(self.calculate_velocity(sprint_id=sprint_id).get("velocity", 0.0))
            except Exception:
                sprint_vel = 0.0

            # average across last 3 sprints
            try:
                avg_vel = float(self.calculate_velocity(sprint_id=None, last_n=3).get("velocity", 0.0))
            except Exception:
                avg_vel = 0.0

            record = {
                "sprint_id": sprint_id,
                "sprint_velocity": sprint_vel,
                "average_velocity": avg_vel,
                "logged_at": _now_iso(),
            }
            try:
                self._append_velocity_log(record)
            except Exception:
                # best-effort logging; don't fail the status update
                pass

            message = f"Sprint completed. Average team velocity: {avg_vel} points."
            return {"message": message, "sprint_velocity": sprint_vel, "average_velocity": avg_vel}

        return {"message": f"Sprint status set to {status}", "sprint_id": sprint_id}

    def manage_sprint_capacity(self, sprint_id: int, member_capacity: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Analyze workload distribution for a sprint with many control paths.

        `member_capacity` is a mapping of member -> max points. If missing, a
        default capacity of 10 points per member is assumed. Uses nested
        conditionals and exception handling to keep cyclomatic complexity high.
        """
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        capacity_map = {}
        if member_capacity is None:
            capacity_map = {}
        else:
            try:
                if isinstance(member_capacity, dict):
                    capacity_map = member_capacity
                else:
                    capacity_map = {}
            except Exception:
                capacity_map = {}

        stories = sprint.get("stories") or []
        member_load: Dict[str, int] = {}
        unassigned: List[Dict[str, Any]] = []
        total_points = 0

        for ref in stories:
            pid = ref.get("project_id")
            sid = ref.get("story_id")
            try:
                story = self._get_story(pid, sid)
            except Exception:
                story = {"assignee": "unknown", "points": 0}

            # derive assignee with multiple branches
            assignee = story.get("assignee")
            if not assignee:
                assignee = story.get("owner") if story.get("owner") else "unassigned"

            # parse points defensively
            pts = 0
            try:
                pts = int(story.get("points", 0) or 0)
            except Exception:
                try:
                    pts = int(float(story.get("points", 0)))
                except Exception:
                    pts = 0

            total_points += pts
            if assignee == "unassigned":
                unassigned.append({"project_id": pid, "story_id": sid, "points": pts})
            else:
                member_load[assignee] = member_load.get(assignee, 0) + pts

        # evaluate load vs capacity with branching heuristics
        assessments: List[Dict[str, Any]] = []
        for member, load in member_load.items():
            cap = 10
            if member in capacity_map:
                try:
                    cap = int(capacity_map.get(member, 10))
                except Exception:
                    cap = 10
            status = "balanced"
            if cap <= 0:
                status = "invalid_capacity"
            else:
                if load > cap:
                    if load >= cap * 1.5:
                        status = "severely_overloaded"
                    else:
                        status = "overloaded"
                elif load == cap:
                    status = "at_capacity"
                else:
                    gap = cap - load
                    if gap <= 2:
                        status = "near_capacity"
                    elif gap <= 5:
                        status = "lightly_loaded"
                    else:
                        status = "underutilized"

            assessments.append({"member": member, "load": load, "capacity": cap, "status": status})

        # overall risk scoring
        risk = "low"
        overloaded = [a for a in assessments if a["status"] in {"overloaded", "severely_overloaded"}]
        if overloaded:
            if any(a["status"] == "severely_overloaded" for a in overloaded):
                risk = "critical"
            elif len(overloaded) >= 2:
                risk = "high"
            else:
                risk = "medium"
        else:
            if unassigned and total_points > 0:
                risk = "medium"
            elif total_points == 0:
                risk = "unknown"
            else:
                risk = "low"

        # propose rebalancing suggestions
        suggestions: List[str] = []
        if unassigned:
            suggestions.append("Assign owners to unassigned stories")
        if risk in {"high", "critical"}:
            suggestions.append("Redistribute stories from overloaded members")
        if not suggestions:
            suggestions.append("No action needed")

        summary = {
            "sprint_id": sprint_id,
            "total_points": total_points,
            "member_load": assessments,
            "unassigned": unassigned,
            "risk": risk,
            "suggestions": suggestions,
            "generated_at": _now_iso(),
        }

        # annotate sprint with capacity analysis history
        sprint.setdefault("capacity_checks", []).append(summary)
        sprint["modified_at"] = _now_iso()
        self.save_data()
        return summary

    def export_sprint_report(self, sprint_id: int, filepath: Optional[str] = None,
                              include_details: bool = True, fmt: str = "json") -> Dict[str, Any]:
        """Export sprint results to a report file with rich branching.

        Supports `json` (default) or `txt` formats. Ensures directories exist
        and handles overwrite logic with extra control flow to keep complexity
        high. Returns metadata about the saved report.
        """
        sprint = self._find_sprint(sprint_id)
        if sprint is None:
            raise ValueError("Sprint not found")

        # resolve path
        base_dir = Path("data/reports")
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        target_fmt = (fmt or "json").lower()
        if target_fmt not in {"json", "txt"}:
            target_fmt = "json"

        if filepath:
            out_path = Path(filepath)
        else:
            default_name = f"sprint_{sprint_id}_report.{target_fmt}"
            out_path = base_dir / default_name

        # assemble data
        report: Dict[str, Any] = {
            "sprint_id": sprint.get("id"),
            "name": sprint.get("name"),
            "start_date": sprint.get("start_date"),
            "end_date": sprint.get("end_date"),
            "capacity": sprint.get("capacity"),
            "generated_at": _now_iso(),
        }

        # attach metrics with defensive calls
        try:
            report["velocity"] = self.calculate_velocity(sprint_id).get("velocity", 0.0)
        except Exception:
            report["velocity"] = 0.0

        try:
            summary = self.view_sprint_summary(sprint_id)
            report["percent_complete"] = summary.get("percent_complete", 0.0)
            if include_details:
                report["stories"] = summary.get("stories", [])
        except Exception:
            report["percent_complete"] = 0.0
            if include_details:
                report["stories"] = []

        # include retrospectives if present
        retros = sprint.get("retrospectives", [])
        if retros:
            try:
                latest_retro = retros[-1]
                report["retrospective"] = latest_retro
            except Exception:
                report["retrospective"] = {}
        else:
            report["retrospective"] = {}

        # convert to desired format and write
        written = False
        try:
            if target_fmt == "json":
                with out_path.open("w", encoding="utf-8") as fh:
                    json.dump(report, fh, indent=2, ensure_ascii=False)
                written = True
            else:
                # txt format
                lines = [
                    f"Sprint: {report.get('name')} ({report.get('sprint_id')})",
                    f"Dates: {report.get('start_date')} -> {report.get('end_date')}",
                    f"Capacity: {report.get('capacity')}",
                    f"Velocity: {report.get('velocity')}",
                    f"Completion: {report.get('percent_complete')}%",
                ]
                if include_details:
                    lines.append("Stories:")
                    for st in report.get("stories", []):
                        try:
                            lines.append(f" - {st.get('title')} (pts={st.get('points')}, progress={st.get('progress')})")
                        except Exception:
                            lines.append(" - <unknown story>")
                if report.get("retrospective"):
                    lines.append("Retrospective:")
                    try:
                        lines.append(f"  Sentiment: {report['retrospective'].get('sentiment')}")
                        lines.append(f"  Priority: {report['retrospective'].get('priority')}")
                    except Exception:
                        lines.append("  <error reading retrospective>")
                with out_path.open("w", encoding="utf-8") as fh:
                    fh.write("\n".join(lines))
                written = True
        except Exception:
            written = False

        status = "saved" if written else "failed"
        return {
            "sprint_id": sprint_id,
            "path": str(out_path),
            "format": target_fmt,
            "status": status,
            "size": out_path.stat().st_size if out_path.exists() and written else 0,
        }


    
__all__ = ["SprintManager"]
