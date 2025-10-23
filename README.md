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


### Branch-Naming Policy
- `main` → stable, graded version  
- `dev` → integration branch  
- `story/<story-id>-<short-desc>` → feature branches for each user story  
  e.g. `story/PRJ-001-create-project`
