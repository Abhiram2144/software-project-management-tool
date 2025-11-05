"""
main.py
Simple command-line interface for interacting with the ProjectManager so you
can view and exercise projects, stories and tasks from the terminal.

Usage: run from the repository root:
  python -m src.main
or
  python src\main.py

The CLI is intentionally small — it demonstrates the user stories by letting
you create/list projects, add stories/tasks, view details, and mark tasks done.
"""
from __future__ import annotations

from typing import Optional

from src import ProjectManager


def _prompt_int(prompt: str) -> Optional[int]:
    v = input(prompt).strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        print("Please enter a valid integer.")
        return None


def main_menu(pm: ProjectManager) -> None:
    while True:
        print("\n=== Software Project Management Tool ===")
        print("1) List projects")
        print("2) Create project")
        print("3) View project details (stories & tasks)")
        print("4) Add story to project")
        print("5) Add task to story")
        print("6) Mark task complete")
        print("7) Exit")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            projects = pm.list_projects()
            if not projects:
                print("No projects found.")
            else:
                for p in projects:
                    print(f"{p['id']}: {p['title']} (owner: {p['owner']}) - {p['story_count']} stories")

        elif choice == "2":
            title = input("Project title: ").strip()
            desc = input("Description: ").strip()
            owner = input("Owner: ").strip()
            try:
                pm.create_project(title=title, description=desc, owner=owner)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            pid = _prompt_int("Project ID: ")
            if pid is None:
                continue
            try:
                proj = pm.get_project(pid)
                print(f"\nProject {proj['id']}: {proj['title']} - {proj.get('description','')}")
                stories = proj.get("stories", [])
                if not stories:
                    print("  No stories")
                else:
                    for s in stories:
                        print(f"  Story {s['id']}: {s['title']} (points: {s.get('points',0)}) progress: {s.get('progress',0.0)}%")
                        tasks = s.get("tasks", [])
                        for t in tasks:
                            print(f"    - {t.get('title')} [{t.get('status')}] assigned: {t.get('assigned_to')} est_hours: {t.get('estimated_hours')}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            pid = _prompt_int("Project ID to add story to: ")
            if pid is None:
                continue
            title = input("Story title: ").strip()
            desc = input("Story description: ").strip()
            pts = _prompt_int("Story points (integer): ")
            if pts is None:
                print("Invalid points")
                continue
            try:
                pm.add_story_to_project(pid, title=title, description=desc, points=pts)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "5":
            pid = _prompt_int("Project ID: ")
            sid = _prompt_int("Story ID: ")
            if pid is None or sid is None:
                continue
            title = input("Task title: ").strip()
            assigned = input("Assigned to: ").strip()
            est = input("Estimated hours (optional): ").strip()
            est_val = float(est) if est else None
            try:
                pm.add_task_to_story(pid, sid, title=title, assigned_to=assigned or None, estimated_hours=est_val)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "6":
            pid = _prompt_int("Project ID: ")
            sid = _prompt_int("Story ID: ")
            if pid is None or sid is None:
                continue
            ttitle = input("Task title to mark complete: ").strip()
            try:
                pm.mark_task_complete(pid, sid, ttitle)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "7":
            print("Goodbye")
            break

        else:
            print("Unknown option. Please try again.")


def run_cli() -> None:
    pm = ProjectManager()
    main_menu(pm)


if __name__ == "__main__":
    run_cli()
