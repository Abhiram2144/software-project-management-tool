
import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from src.project_manager.project_manager import ProjectManager, ValidationError
from src.sprint_manager import SprintManager
from src.export_metrics import export_all_metrics
from src.dashboard_generator import generate_dashboard


def _as_dict(obj: Any) -> Any:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj


def _emit(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for software-project-management-tool")
    parser.add_argument("--data-file", default=None, help="Path to projects JSON (default: data/projects.json)")
    parser.add_argument("--sprint-data-file", default=None, help="Path to sprints JSON (default: data/sprints.json)")
    parser.add_argument("--menu", action="store_true", help="Launch interactive menu instead of single command")

    return parser


def prompt(msg: str, allow_empty: bool = False) -> str:
    while True:
        val = input(msg).strip()
        if val or allow_empty:
            return val
        print("Value cannot be empty. Try again.")

"""Menu-driven CLI for projects, stories, tasks, sprints, and metrics."""
import argparse
import json
import sys
from typing import Dict, List, Optional

from src.project_manager.project_manager import ProjectManager, ValidationError
from src.sprint_manager import SprintManager
from src.export_metrics import export_all_metrics
from src.dashboard_generator import generate_dashboard


def _emit(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for software-project-management-tool")
    parser.add_argument("--data-file", default=None, help="Path to projects JSON (default: data/projects.json)")
    parser.add_argument("--sprint-data-file", default=None, help="Path to sprints JSON (default: data/sprints.json)")
    parser.add_argument("--menu", action="store_true", help="Launch interactive menu (required)")
    return parser


def prompt(msg: str, allow_empty: bool = False) -> str:
    while True:
        val = input(msg).strip()
        if val or allow_empty:
            return val
        print("Value cannot be empty. Try again.")


def prompt_int(msg: str, allow_empty: bool = False) -> Optional[int]:
    while True:
        val = input(msg).strip()
        if not val and allow_empty:
            return None
        try:
            return int(val)
        except ValueError:
            print("Enter a valid integer.")


def _parse_member_capacity(items: Optional[List[str]]) -> Dict[str, int]:
    cap: Dict[str, int] = {}
    if not items:
        return cap
    for entry in items:
        if ":" not in entry:
            continue
        name, pts = entry.split(":", 1)
        name = name.strip()
        try:
            cap[name] = int(pts)
        except Exception:
            continue
    return cap


def interactive_menu(pm: ProjectManager, sm: SprintManager) -> None:
    menu = {
        "1": "Create project",
        "2": "List projects",
        "3": "Add story",
        "4": "Edit story",
        "5": "Delete story",
        "6": "Add task",
        "7": "Complete task",
        "8": "Save data",
        "9": "Load data",
        "10": "Create sprint",
        "11": "Assign story to sprint",
        "12": "Sprint velocity",
        "13": "Sprint summary",
        "14": "Sprint burndown",
        "15": "Sprint capacity",
        "16": "Sprint retrospective",
        "17": "Export sprint report",
        "18": "Recalculate velocity",
        "19": "Generate metrics dashboard",
        "0": "Quit",
    }

    while True:
        print("\n==== Project Manager Menu ====")
        for k, v in sorted(menu.items(), key=lambda x: int(x[0])):
            print(f"{k}. {v}")
        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                title = prompt("Project title: ")
                owner = prompt("Owner: ")
                desc = prompt("Description (optional): ", allow_empty=True)
                _emit(pm.create_project(title, desc, owner))

            elif choice == "2":
                verbose = input("Verbose? (y/N): ").strip().lower().startswith("y")
                if verbose:
                    pm.load_data()
                    _emit(pm._data)
                else:
                    _emit(pm.list_projects())

            elif choice == "3":
                pid = prompt_int("Project ID: ")
                title = prompt("Story title: ")
                desc = prompt("Description (optional): ", allow_empty=True)
                pts = prompt_int("Points: ")
                _emit(pm.add_story_to_project(pid, title, desc, pts))

            elif choice == "4":
                pid = prompt_int("Project ID: ")
                sid = prompt_int("Story ID: ")
                title = prompt("New title (blank to skip): ", allow_empty=True)
                desc = prompt("New description (blank to skip): ", allow_empty=True)
                pts = prompt_int("New points (blank to skip): ", allow_empty=True)
                title_arg = title if title else None
                desc_arg = desc if desc else None
                _emit(pm.edit_story(pid, sid, title=title_arg, description=desc_arg, points=pts))

            elif choice == "5":
                pid = prompt_int("Project ID: ")
                sid = prompt_int("Story ID: ")
                _emit(pm.delete_story(pid, sid))

            elif choice == "6":
                pid = prompt_int("Project ID: ")
                sid = prompt_int("Story ID: ")
                title = prompt("Task title: ")
                assigned = prompt("Assigned to (optional): ", allow_empty=True)
                est = prompt("Estimated hours (optional): ", allow_empty=True)
                est_arg: Optional[str] = est if est else None
                assigned_arg: Optional[str] = assigned if assigned else None
                _emit(pm.add_task_to_story(pid, sid, title, assigned_to=assigned_arg, estimated_hours=est_arg))

            elif choice == "7":
                pid = prompt_int("Project ID: ")
                sid = prompt_int("Story ID: ")
                ident = prompt("Task id or title: ")
                ident_arg = int(ident) if ident.isdigit() else ident
                by = prompt("Completed by (optional): ", allow_empty=True) or None
                force = input("Force? (y/N): ").strip().lower().startswith("y")
                cascade = input("Cascade? (y/N): ").strip().lower().startswith("y")
                _emit(pm.mark_task_complete(pid, sid, task_identifier=ident_arg, by=by, force=force, cascade=cascade))

            elif choice == "8":
                no_backup = input("Skip backup? (y/N): ").strip().lower().startswith("y")
                _emit({"saved": pm.save_project_data(backup=not no_backup)})

            elif choice == "9":
                restore = input("Attempt restore from backup if needed? (y/N): ").strip().lower().startswith("y")
                _emit(pm.load_project_data(restore_backup=restore))

            elif choice == "10":
                name = prompt("Sprint name: ")
                start = prompt("Start date (YYYY-MM-DD): ")
                end = prompt("End date (YYYY-MM-DD): ")
                cap = prompt_int("Capacity (points): ")
                _emit(sm.create_sprint(name, start, end, cap))

            elif choice == "11":
                pid = prompt_int("Project ID: ")
                sid = prompt_int("Story ID: ")
                spid = prompt_int("Sprint ID: ")
                _emit(sm.add_story_to_sprint(pid, sid, spid))

            elif choice == "12":
                sid = prompt_int("Sprint ID (blank for avg): ", allow_empty=True)
                last_n = prompt_int("Last N sprints (default 3): ", allow_empty=True) or 3
                _emit(sm.calculate_velocity(sid, last_n))

            elif choice == "13":
                sid = prompt_int("Sprint ID: ")
                _emit(sm.view_sprint_summary(sid))

            elif choice == "14":
                sid = prompt_int("Sprint ID: ")
                _emit(sm.generate_burndown_chart(sid))

            elif choice == "15":
                sid = prompt_int("Sprint ID: ")
                raw = input("Member capacities (member:points, comma separated, optional): ").strip()
                items = [r.strip() for r in raw.split(",") if r.strip()]
                caps = _parse_member_capacity(items)
                _emit(sm.manage_sprint_capacity(sid, caps))

            elif choice == "16":
                sid = prompt_int("Sprint ID: ")
                ww = input("Went well (comma separated, optional): ").split(",")
                wp = input("Went poorly (comma separated, optional): ").split(",")
                imp = input("Improvements (comma separated, optional): ").split(",")
                ww = [w.strip() for w in ww if w.strip()]
                wp = [w.strip() for w in wp if w.strip()]
                imp = [w.strip() for w in imp if w.strip()]
                _emit(sm.track_sprint_retrospective(sid, ww, wp, imp))

            elif choice == "17":
                sid = prompt_int("Sprint ID: ")
                fmt = input("Format json/txt (default json): ").strip().lower() or "json"
                path = input("Custom path (optional): ").strip() or None
                include_details = not input("Skip story details? (y/N): ").strip().lower().startswith("y")
                _emit(sm.export_sprint_report(sid, filepath=path, include_details=include_details, fmt=fmt))

            elif choice == "18":
                sid = prompt_int("Sprint ID (blank for avg): ", allow_empty=True)
                last_n = prompt_int("Last N sprints (default 3): ", allow_empty=True) or 3
                _emit(sm.calculate_velocity(sid, last_n))

            elif choice == "19":
                export_all_metrics()
                generate_dashboard()
                print("Dashboard generated at docs/metrics/dashboard_report.html")

            elif choice == "0":
                print("Goodbye!")
                return

            else:
                print("Invalid choice. Try again.")

        except ValidationError as ve:
            print(json.dumps({"error": ve.to_dict()}, indent=2, ensure_ascii=False))
        except Exception as exc:
            print(json.dumps({"error": str(exc)}, indent=2, ensure_ascii=False))


def main(argv: Optional[list[str]] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    pm = ProjectManager(data_file=args.data_file)
    sm = SprintManager(data_file=args.sprint_data_file)

    if args.menu:
        interactive_menu(pm, sm)
        return 0

    print("Interactive mode only. Run with --menu.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
