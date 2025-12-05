## 1. Requirements Management (Sprint 0)



## Software Project Management Tool — CMMI Level 2 Process Description

Last updated: 2025-11-25

This document describes how the Software Project Management Tool project implements CMMI Level 2 process areas for disciplined, repeatable delivery. It captures the Sprint 0 setup, roles, artifacts, control points, and measurable quality gates that the team follows.

Audience
- Project team (developers, testers, scrum master)
- Project manager and stakeholders
- Assessors and auditors

Goals
- Establish disciplined requirements management, project planning and tracking mechanisms.
- Ensure configuration management, QA, and measurement practices are in place for predictable delivery.
- Provide traceability from requirements to implementation and tests.

Principles
- Keep processes lightweight and evidence-driven: every requirement, plan, and change is recorded in the repository or `data/` folder.
- Prefer automation (CI, tests, linters) to enforce quality gates.
- Incremental development using time-boxed sprints with retrospectives.

---

## 1. Process Areas (Level 2)

This project implements the following CMMI Level 2 process areas adapted to an agile workflow.

1. Requirements Management (REQM)
2. Project Planning (PP)
3. Project Monitoring & Control (PMC)
4. Measurement and Analysis (MA)
5. Configuration Management (CM)
6. Process and Product Quality Assurance (PPQA)

Each area maps to specific artifacts, owners, and practices documented below.

---

## 2. Sprint 0 — Setup and Requirements Management

Sprint objective
- Establish the project's scope, repository layout, branch strategy, backlog, and sprint cadence. Prepare measurable metrics and basic CI tooling.

Key outcomes (Sprint 0)
- Backlog: 27 user stories written and prioritized, stored in `/docs/sprint0/user-stories.txt`.
- Team assignment: stories assigned to three members (Abhiram — core backend, Charan — sprints & velocity, Roshan — metrics & testing).
- Planning artifacts: `planning_poker.png`, capacity charts and GitHub Project Board snapshots placed under `/docs/sprint0/`.
- Repository layout: `src/`, `data/`, `docs/`, `test/` with package entrypoints under `src/__init__.py`.
- Branching strategy: feature branches (`feature/XXX-xxxxx`), protected `main` and `development` branches.

Sprint cadence and durations
- Sprint length: 10 working days for Sprint 1 (dates documented in sprint planning notes). Subsequent sprints vary slightly to match academic schedule.

Acceptance criteria for Sprint 0
- Backlog exists and is review-ready.
- Minimum reproducible project scaffold in `src/` and `test/` with at least one passing unit test locally.
- Developer environment instructions added to `README.md`.

Evidence and traceability
- All artifacts referenced above are stored in `docs/sprint0/`. Each story ID maps to related issues and branches. A traceability table is maintained in `docs/sprint0/traceability.md` (recommended).

---

## 3. Roles & Responsibilities

- Project Manager (Abhiram)
	- Oversees planning, acceptance, and CI configuration. Owner of `REQM`, `PP`, and `MA` artifacts.
- Scrum Master (Abhiram)
	- Facilitates sprint planning, retrospectives, and enforces the Definition of Done for sprints.
- Developers (Abhiram, Charan, Roshan)
	- Implement features, write unit tests, and maintain module-level documentation.
- QA / Metrics Lead (Roshan)
	- Implements metrics functions (PERT, COCOMO), testing harnesses, and ensures tests map to acceptance criteria.

Each PR must include: story ID, short description, list of files changed, linked issue, and a checklist (docs, tests, CC check, CI green).

---

## 4. Project Planning (PP)

Planning artifacts
- Backlog: `/docs/sprint0/user-stories.txt`
- Sprint plans: each sprint folder under `/docs/sprints/` containing scope, dates, capacity, and selected stories.
- Estimation: story points via Planning Poker recorded as `planning_poker.png`.

Planning steps
1. Groom backlog and break epics into stories (owner: PM).
2. Estimate using Planning Poker with at least two estimations per story.
3. Assign stories to team members and select sprint scope using capacity chart.

Deliverables
- Sprint plan (start/end, capacity, stories selected) recorded before sprint start.

---

## 5. Project Monitoring & Control (PMC)

Monitoring practices
- Daily status updates (standups) captured briefly as GitHub issue comments or sprint board updates.
- Sprint burndown tracked in `/docs/sprint0/burndown/` (generated artifact planned for Sprint 2).

Control gates
- Definition of Done (DoD):
	- Code merged to `development` or `main` only via PR.
	- All unit tests passing and coverage not decreasing.
	- Linters (flake8) and formatters (black) are applied.
	- Documentation (module-level docstrings) present for public functions.

Escalation
- If a critical story slips or a blocker occurs, notify PM and schedule a mid-sprint planning adjustment.

---

## 6. Measurement & Analysis (MA)

Planned metrics
- Velocity (completed story points per sprint).
- Test coverage (pytest-cov) per module.
- Cyclomatic complexity (radon) — track average CC per module and per-function hotspots.
- Lead time and cycle time can be derived from GitHub timestamps.

Storage and reporting
- Metrics results saved under `/docs/metrics/` as JSON and HTML summary files. Metric functions are implemented in `src/metrics_engine.py` (Member C).

Quality targets
- Test coverage: target >= 85% across `src/` for production merges.
- CC: no new functions added with CC > 12 without reviewer justification.

---

## 7. Configuration Management (CM)

Repository conventions
- Branching: `main` (protected), `development` (integration), `feature/*` for individual stories.
- Tagging: releases tagged with semantic versioning (vMAJOR.MINOR.PATCH).

Artifact control
- All persistent runtime data lives under `data/` and is not tracked (gitignored) unless example fixtures are necessary; schema definitions are tracked under `docs/`.

Change control
- PRs provide a clear description and link to story/issue. Major design changes require an ADR (Architecture Decision Record) under `docs/adr/`.

---

## 8. Process and Product Quality Assurance (PPQA)

QA checklist (to be enforced via PR template and CI)
1. Tests added/updated for new behavior.
2. Docstrings for public functions.
3. Linting (`flake8`) and formatting (`black`) passed.
4. Cyclomatic complexity (radon) measured; any function >12 requires documented justification.
5. Code reviewed by at least one other team member.

Automated gates
- GitHub Actions will run on PRs:
	- `pytest --maxfail=1 --disable-warnings -q`
	- `pytest --cov=src --cov-report=xml`
	- `flake8` and `black --check`
	- `radon cc -s src | tee radon-report.txt` (fail CI if new violations)

---

## 9. Sprint 0 Artifacts & Evidence (location)

- Backlog: `/docs/sprint0/user-stories.txt`
- Planning Poker evidence: `/docs/sprint0/planning_poker.png`
- Capacity charts: `/docs/sprint0/team-capacity-with-priorities.png`
- Project board snapshot: `/docs/sprint0/project-board.png`
- Repo layout & branch strategy: `/docs/sprint0/repo-structure.png`, `/docs/sprint0/branch-strategy.png`
- Sprint retrospective notes: `/docs/sprint0/retrospective.md` (also included in sprint0 user-stories file)

If any artifact is missing, create a minimal placeholder and update the sprint retrospective with a link.

---

## 10. Templates and Checklists

PR template (use when opening PR)
```
Title: [STORY-ID] Short title

Description:
- Link to issue: #123
- Summary of changes:

Checklist:
- [ ] Tests added/updated
- [ ] Docstrings present for public methods
- [ ] flake8 / black passed
- [ ] radon CC checked (no new > 12)
- [ ] CI green
```

Definition of Done (DoD)
- Code implements acceptance criteria in the story.
- Tests pass and coverage does not decrease.
- Peer-reviewed and merged via PR.

---

## 11. Next steps and Continuous Improvement

Short-term actions (Sprint 2 planning)
- Implement CI pipeline with tests and coverage checks (owner: Abhiram).
- Roshan and Charan to refactor their modules (owners: Roshan, Charan) to add comments, lower CC, and add unit tests — owners to add progress to `docs/sprint0/retrospective.md`.
- Create `CONTRIBUTING.md` and `CHANGELOG.md` (owner: Abhiram).

Long-term improvements
- Add automated burndown chart generation and velocity logging.
- Add `test_registry` to catalog tests and test outcomes across modules.

---

This document is the authoritative Level 2 process description for the project. It should be reviewed and updated at the start of each sprint by the Project Manager and Scrum Master.
- /docs/sprint0/planning-poker/






---

## 12. Sprint 1 — Completion & Retrospective

Sprint: 1

Sprint end date: 2025-11-24

Retrospective prepared: 2025-11-25

**What Went Well**
- **Completed Stories**: The team delivered the planned user stories for Sprint 1:
  - Abhiram: `PRJ-001` (Create New Project), `PRJ-002` (View All Projects), `STY-001` (Add User Story).
  - Charan: `SPR-001` (Create Sprint), `SPR-002` (Assign Stories to Sprint), `SPR-003` (Calculate Sprint Velocity).
  - Roshan: `MET-001` (Calculate PERT), `MET-002` (COCOMO I), `MET-003` (COCOMO II).
- **Persistence & Basic APIs**: Project and sprint persistence implemented under `data/` and exposed via the `ProjectManager` and `SprintManager` APIs enabling other modules to integrate.

**What Didn't Go Well**
- **Late Submissions**: Some contributors submitted their work after the sprint end (24 Nov), which reduced review and integration time.
- **Code Quality & Structure**: Several modules lack module-level docstrings, inline comments, and clear separation of concerns; this slowed reviews.
- **Cyclomatic Complexity**: Multiple functions exceed the desired complexity threshold and should be refactored into smaller units.
- **Insufficient Tests**: Edge cases and branch coverage are missing in several modules; overall coverage must be improved before merging.

**Root Causes / Observations**
- Insufficient time allocated for documentation and tests after feature implementation.
- No mandatory pre-merge checklist or CI gates enforced at merge time.
- No reserved peer-review time before the sprint end.

**Action Items (Concrete, Owner, Due Date)**
1. **Refactor & Comment Roshan's Metric Modules** — Owner: Roshan — Due: 2025-12-01
	- Add module-level docstrings, function docstrings, and inline comments explaining non-obvious logic.
	- Break up functions whose cyclomatic complexity (CC) > 10 into smaller helper functions.
	- Add type hints to public functions.
	- Add unit tests (happy path and edge cases) for PERT and COCOMO functions.

2. **Refactor & Structure Charan's Sprint Modules** — Owner: Charan — Due: 2025-12-01
	- Improve structure in `src/sprint_manager` (clear separation of persistence, domain logic, and integrations).
	- Add docstrings, input validation, and unit tests for `create_sprint`, `add_story_to_sprint`, and `calculate_velocity`.
	- Reduce CC in functions flagged by the static analyzer; aim for CC <= 10 per function.

3. **Establish a Minimal CI Pipeline** — Owner: Abhiram — Due: 2025-12-05
	- Add GitHub Actions workflow to run `pytest --cov=src` and fail PRs with coverage < 85%.
	- Run linters (`flake8`) and formatters (`black`) on push.
	- Add a radon CC check and fail the build if new functions exceed CC threshold (suggested 12).

4. **Introduce a PR Checklist & Template** — Owner: Abhiram — Due: 2025-11-30
	- Checklist items: docstrings added, tests added, CC measured and acceptable, `requirements.txt` updated (if any), and `README` or docs updated where applicable.

5. **Add Targeted Unit Tests & Improve Coverage** — Owner: All contributors — Due: 2025-12-05
	- Each contributor must add unit tests for their sprint 1 modules covering normal cases and edge cases.
	- Aim for module-level coverage >= 85% before merging into `main`.

6. **Schedule Peer Review Sessions** — Owner: Scrum Master (Charan) — Due: schedule by 2025-11-28
	- Reserve 1–2 hours for code walkthroughs before the sprint end to catch early issues and avoid last-minute fixes.

**Quality Gates (Required for next sprints)**
- Every PR must pass automated tests and linters before it can be merged.
- Add a `CHANGELOG.md` entry for each merged story describing the change briefly.
- Enforce `black` formatting and `flake8` linting via CI.

**Follow-up / Backlog Items**
- Add a task to the backlog to implement `test_registry` for tracking test outcomes and historical velocities.
- Create a task to generate a developer-facing `CONTRIBUTING.md` describing branch naming, PR checklist, and coding standards.

**Final Notes**
- The team completed the planned functional work for Sprint 1, but non-functional quality aspects (docs, tests, complexity) must be prioritized for Sprint 2. The action items above are intended to be small, verifiable tasks that improve maintainability and speed up future reviews.

---

## 13. Sprint 2 — Completion & Retrospective

Sprint: 2

Sprint end date: 2025-12-05

Retrospective prepared: 2025-12-05

Sprint objective
- Implement quality improvements (docstrings, input validation, tests) and finalize behavior changes introduced in Sprint 1 (archive/delete semantics, task creation).

Key outcomes (Sprint 2)
- Added docstrings and input validation to multiple modules; improved `ProjectManager` with `edit_story`, `delete_story`, and `add_task_to_story` implementations.
- Created `docs/Sprint2/Sprint_Retrospective.txt` capturing Sprint 2 findings and action items.
- CI baseline work started (draft workflow on `ci/setup` branch) and quality gates defined for next sprint.

What Went Well
- Non-functional work received attention: documentation and some validation were added across the codebase.
- New story and task APIs implemented and available for integration and testing.
- Team awareness of complexity and coverage goals increased; action items were created to address gaps.

What Didn't Go Well
- Unit tests still lag behind implementation; many new branches and edge cases remain untested.
- Some behavioral changes (soft-delete/archive) require API documentation and explicit migration notes.
- CI workflow is draft-level and needs finalization and enforcement on PRs.

Action Items (Concrete, Owner, Due Date)
1. **Add Missing Unit Tests for Story & Task Methods** — Owner: All contributors — Due: 2025-12-12
	- Cover `edit_story` branches, `delete_story` archive and cascade behaviors, and `add_task_to_story` edge cases.

2. **Document Soft-Delete / Archive Behavior** — Owner: Abhiram — Due: 2025-12-09
	- Update `docs/` and public docstrings to describe archived vs deleted story semantics.

3. **Finalize CI & Quality Gates** — Owner: Abhiram — Due: 2025-12-12
	- Merge and enable GitHub Actions to run `pytest --cov=src`, `flake8`, `black --check`, and `radon cc` on PRs.

4. **Refactor High-CC Functions** — Owner: Roshan & Charan — Due: 2025-12-15
	- Break up functions with CC > 12 and add tests to cover helper functions.

5. **Enforce PR Checklist and Review Window** — Owner: Charan — Due: 2025-12-08
	- Require reviewers and a short review window before merges.

Quality Gates (Sprint 3 prerequisites)
- All new functionality must be accompanied by unit tests covering relevant branches and edge cases.
- Coverage and CC checks must be active in CI for PR blocking.

Follow-up / Backlog Items
- Create `CONTRIBUTING.md` and `CHANGELOG.md` (Owner: Abhiram) — Due: 2025-12-10
- Implement `test_registry` for tracking test outcomes and historical velocities (Owner: Roshan) — Due: 2026-01-05

Final Notes
- Sprint 2 closed several important gaps but made clear the priority for Sprint 3 is tests, CI stabilization, and targeted refactoring to reduce complexity while keeping the implemented features intact.





