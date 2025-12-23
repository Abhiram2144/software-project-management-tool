# software-project-management-tool
Backend-only Python application for CO7095 – Software Measurement &amp; Quality Assurance 2025/26. Implements Agile, PERT, COCOMO, EVM, symbolic &amp; concolic testing.

# Clone repo
git clone https://github.com/Abhiram2144/software-project-management-tool.git

# To Create dev branch
```bash
 git checkout -b dev
 git push -u origin dev
```

# To Create story branch
```bash
git checkout dev
git checkout -b story/<ID>-<desc>
git push -u origin story/<ID>-<desc>
```

# Merge story branch -> dev via PR
# Merge dev -> main only after sprint completion


### Setup (after unzip)
```powershell
# From repo root
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

### Run the app (metrics pipeline)
```powershell
# From repo root, after activation
python src/export_metrics.py
python src/dashboard_generator.py
# Outputs: metrics/*.json and docs/metrics/dashboard_report.html
```

### Run the CLI (menu only)
```powershell
python -m src.cli --menu
# Menu covers project CRUD, stories/tasks, sprint ops (create/assign/velocity/summary/burndown/capacity/retro/report), and metrics dashboard
```

### Run tests
```powershell
# From repo root, after activation
python -m unittest discover as1809/test
```


### Branch-Naming Policy
- `main` → stable, graded version  
- `dev` → integration branch  
- `story/<story-id>-<short-desc>` → feature branches for each user story  
  e.g. `story/PRJ-001-create-project`
