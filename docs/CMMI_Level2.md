# CMMI Level 2 Documentation Framework  
*(CO7095 – Software Measurement & Quality Assurance | Project: Software Project Management Tool)*  

---

## 1. Requirements Management  
We maintain a structured set of user stories to capture all functional and non-functional requirements.  
- Each story follows the *As a / I want to / So that* template.  
- All stories are created as GitHub Issues and linked to commits, pull requests, and test cases.  
- Stories are organized on the GitHub Project Board under **Backlog → Sprint Columns → Done** for full traceability.  

**Evidence**  
- `/docs/sprint0/userstories_list.png` – complete issue list  
- `/docs/sprint0/projectboard_backlog.png` – backlog before Sprint 1  

---

## 2. Project Planning  

### Sprint Schedule  

| Sprint | Duration | Focus | Stories | Points | Owners |
|:--|:--|:--|:--|:--|:--|
| **1** | Oct 22 – Nov 4 | Core backend, CLI, JSON persistence, black-box tests | 6 (3 each) | 22 | Abhiram & Roshan |
| **2** | Nov 5 – Nov 18 | Sprint linking, velocity calc, white-box tests | 6 (3 each) | 26 | Abhiram & Roshan |
| **3** | Nov 19 – Dec 2 | Metrics engine (PERT, COCOMO I/II, EVM) | 5 (2–3 each) | 22 | Abhiram & Roshan |
| **4** | Dec 3 – Dec 15 | Symbolic + Concolic testing, QA, final docs & video | 5 (2–3 each) | 24 | Abhiram & Roshan |

### Planning Artifacts  
- **Story-Point Estimation:** done via online Planning Poker (see `/docs/sprint0/planning_poker_sprint0.png`).  
- **Tools & Tech:** Python 3.11 +, PyCharm IDE, pytest, GitHub Projects.  
- **Velocity Target:** ~22–25 points per sprint.  
- **Risk Register:** schedule delays, test coverage risks, and metric accuracy to be reviewed at each sprint retro.  

---

## 3. Project Monitoring & Control  
Project progress is monitored using quantitative metrics and visual dashboards.  
- **Burndown Chart:** created at the start and end of every sprint.  
- **Velocity Tracking:** derived from completed story points / sprint.  
- **Earned Value Management (EVM):** PV, EV, AC tracked in `/docs/metrics/`.  
- **Review Cadence:** bi-weekly stand-ups; sprint retros logged in README.  

**Evidence (to be added)**  
- `/docs/sprint1/burndown_start.png`  
- `/docs/sprint2/burndown_end.png`  
- `/docs/sprint3/velocity_chart.png`  
- `/docs/sprint3/evm_results.png`  

---

## 4. Configuration Management  
Configuration is controlled through GitHub branches, pull requests, and version tags.  
- **Branching Policy:**  
  - `main` – stable release branch (protected)  
  - `dev` – integration branch  
  - `story/<id>-<short-desc>` – feature/user story branches  
- **Rules:** require review before merge; one approver minimum; no direct push to main.  
- **Version Tags:** `sprint0`, `sprint1`, `sprint2`, `sprint3`, `sprint4`.  

**Evidence**  
- `/docs/sprint0/branches_proof.png`  
- `/docs/sprint0/sprint0_tag.png`  
- PR screenshots each sprint.  

---

## 5. Process & Product Quality Assurance  
Quality assurance is maintained through structured testing and peer reviews.  

| Test Type | Focus | Tool | Owner | Sprint |
|:--|:--|:--|:--|:--|
| Black-Box | Functional behavior | pytest | Abhiram | 1 |
| White-Box | Logic branches & coverage | pytest-cov | Roshan | 2 |
| Symbolic | Path conditions & constraints | z3-solver (optional) | Abhiram | 4 |
| Concolic | Mixed symbolic/concrete execution | Custom Python module | Roshan | 4 |

**QA Checklist**  
- Minimum coverage ≥ 85 % by Sprint 4.  
- All test failures documented with root cause analysis.  
- Peer code review for every PR before merge.  

---

## 6. Measurement & Analysis  
Software measurement is central to the project’s academic outcome.  

| Metric | Purpose | Implementation Location |
|:--|:--|:--|
| **PERT** | Estimate expected task duration & variance | `metrics_engine.calculate_pert()` |
| **COCOMO I/II** | Estimate cost & effort from project size | `metrics_engine.calculate_cocomo()` |
| **EVM** | Monitor schedule & cost performance (CPI/SPI) | `metrics_engine.compute_evm()` |
| **Velocity** | Team productivity measurement | `sprint_manager.calculate_velocity()` |

Evidence screenshots and charts will reside in `/docs/metrics/` after Sprint 3.  

---

## 7. Sprint Evidence Index  
| Sprint | Folder | Key Artifacts |
|:--|:--|:--|
| **0** | `/docs/sprint0` | Repo setup, user stories, CMMI skeleton, branch rules |
| **1** | `/docs/sprint1` | Core backend code, CLI demo, black-box tests |
| **2** | `/docs/sprint2` | Sprint linking, velocity calc, white-box coverage |
| **3** | `/docs/sprint3` | PERT, COCOMO, EVM charts, metrics validation |
| **4** | `/docs/sprint4` | Symbolic & Concolic testing, final QA, report & video |

---

## 8. Continuous Improvement Statement  
After each sprint, a short retrospective is logged in `README.md` covering:  
- What went well  
- What can be improved  
- Actions for next sprint  

This cycle ensures progressive maturity toward CMMI Level 2 compliance and lays the foundation for Level 3 standardization in future projects.  
