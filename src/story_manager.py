"""
story_manager - thin wrapper for story-related operations for Sprint 1.

This module exposes `add_user_story` which delegates to ProjectManager.
"""
from __future__ import annotations

from typing import Dict, Optional

from .project_manager import ProjectManager


_pm = ProjectManager()


def add_user_story(project_id: int, title: str, description: str, story_points: int) -> Dict:
    """Add a new user story to the given project.

    Returns the created story dict or raises ValueError on invalid input.
    """
    return _pm.add_story_to_project(project_id, title=title, description=description, points=story_points)


__all__ = ["add_user_story"]
