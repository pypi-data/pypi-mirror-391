# Project Intelligence Skill

## Purpose

This skill enables CCPM to automatically understand your project's structure, tools, and configuration. When invoked, CCPM will examine your project's configuration files, detect installed tools, understand your CI/CD setup, and store this knowledge for use throughout your development workflow.

## What This Skill Does

When you invoke this skill, CCPM will:

1. **Parse project configuration files** (pyproject.toml, package.json, etc.)
2. **Detect CLI tools and package managers** (yarn, npm, make, poetry, etc.)
3. **Understand monorepo/multi-project structures**
4. **Analyze CI/CD workflows** (GitHub Actions, GitLab CI, etc.)
5. **Store learned configuration** in `.claude/learned/` for persistent use

## When to Use This Skill

**Invoke at project initialization:**
```
/skill project-intelligence
```

**Or when project configuration changes:**
- After adding new tools to pyproject.toml
- After changing package manager (npm → yarn)
- After adding/modifying CI workflows
- After restructuring monorepo

## How It Works

### Feature 1: Pyproject.toml Auto-Configuration

**Goal:** Automatically configure CCPM to use project's exact tool settings.

**Instructions for CCPM:**

When this skill is invoked or during project initialization:

1. **Read pyproject.toml** if it exists in project root
2. **Extract configuration sections:**
   - `[tool.pytest]` - Test framework configuration (markers, options, test paths)
   - `[tool.ruff]` - Linting rules (line-length, select rules, ignore rules)
   - `[tool.mypy]` - Type checking configuration
   - `[tool.black]` or `[tool.ruff.format]` - Code formatting configuration
   - `[project]` - Project metadata (name, version, dependencies)
   - `[tool.poetry]` - Poetry-specific settings if present

3. **Store in `.claude/learned/project-config.json`:**
   ```json
   {
     "test": {
       "framework": "pytest",
       "command": "pytest -v",
       "markers": ["slow", "integration"],
       "test_paths": ["tests/"],
       "options": ["--html=report.html"]
     },
     "lint": {
       "tool": "ruff",
       "command": "ruff check .",
       "line_length": 88,
       "select": ["E", "F", "W"],
       "ignore": ["E501"]
     },
     "format": {
       "tool": "ruff",
       "command": "ruff format .",
       "line_length": 88
     },
     "typecheck": {
       "tool": "mypy",
       "command": "mypy .",
       "strict": true
     }
   }
   ```

4. **Use this configuration** in all subsequent CCPM operations:
   - When testing: use exact command from config (`test.command`)
   - When linting: respect line-length and rules from config
   - When formatting: use project's preferred formatter
   - When type checking: use mypy settings from config

**Success Criteria:**
- All CCPM operations respect project's tool configuration from pyproject.toml
- Agents use `ruff check` with correct options, not hardcoded assumptions
- Test commands match project's pytest configuration exactly

---

### Feature 2: CLI Tool Detection & Reference Generation

**Goal:** Detect all project management tools and document their usage.

**Instructions for CCPM:**

Detect and document all project management tools:

1. **Detect package manager:**
   - Check for `yarn.lock` → yarn
   - Check for `package-lock.json` → npm
   - Check for `pnpm-lock.yaml` → pnpm
   - Check for `poetry.lock` → poetry
   - Check for `Pipfile` → pipenv
   - Check for `requirements.txt` + no other markers → pip
   - Store primary tool

2. **Parse Makefile** (if exists):
   - Extract all targets: `grep '^[a-zA-Z0-9_-]*:' Makefile`
   - Document target purposes from comments above targets
   - Example: `# Build production bundle` → `build` target

3. **Parse package.json scripts** (if exists):
   - Extract all script commands from `"scripts"` section
   - Map common patterns:
     - `"test": "jest"` → test command
     - `"build": "webpack"` → build command
     - `"lint": "eslint ."` → lint command
     - `"format": "prettier --write ."` → format command
     - `"dev": "vite"` → dev server command

4. **Store in `.claude/learned/cli-tools.json`:**
   ```json
   {
     "package_manager": "yarn",
     "detected_at": "2025-11-13T12:00:00Z",
     "commands": {
       "install": "yarn install",
       "test": "yarn test",
       "build": "yarn build",
       "lint": "yarn lint",
       "format": "yarn format",
       "dev": "yarn dev"
     },
     "makefile_targets": {
       "test": "Run test suite",
       "build": "Build production bundle",
       "clean": "Remove build artifacts",
       "deploy": "Deploy to production"
     }
   }
   ```

5. **Provide to agents:** When agents need to run commands, they read this file and use project's actual commands, never hardcoded assumptions.

**Success Criteria:**
- Agents always use `yarn test` if yarn is detected, not `npm test`
- Makefile targets are documented and accessible to agents
- No hardcoded tool assumptions in CCPM operations

---

### Feature 4: Multi-Entry Point & Monorepo Detection

**Goal:** Understand if project has multiple subprojects or is a monorepo.

**Instructions for CCPM:**

Detect if project is a monorepo or has multiple entry points:

1. **Check for workspace patterns:**
   - `package.json` with `"workspaces"` field → Yarn/npm workspaces
   - `pnpm-workspace.yaml` exists → pnpm workspaces
   - `lerna.json` exists → Lerna monorepo
   - `nx.json` exists → Nx monorepo
   - Multiple `pyproject.toml` files in subdirectories → Python monorepo
   - Multiple `Cargo.toml` files → Rust workspace

2. **Map subproject structure:**
   - Find all `package.json` or `pyproject.toml` files recursively
   - Extract project names from each config file
   - Determine relative paths from repo root
   - Infer project types:
     - Has React/Vue dependencies → frontend
     - Has FastAPI/Flask/Django → backend
     - Is library package → library
     - Has CLI entry point → cli-tool

3. **Store in `.claude/learned/project-structure.json`:**
   ```json
   {
     "type": "monorepo",
     "tool": "yarn-workspaces",
     "detected_at": "2025-11-13T12:00:00Z",
     "root_path": "/path/to/project",
     "subprojects": [
       {
         "name": "frontend",
         "path": "packages/frontend",
         "type": "react-app",
         "config_file": "packages/frontend/package.json",
         "test_command": "yarn workspace frontend test",
         "build_command": "yarn workspace frontend build"
       },
       {
         "name": "backend",
         "path": "packages/backend",
         "type": "fastapi",
         "config_file": "packages/backend/pyproject.toml",
         "test_command": "cd packages/backend && pytest",
         "build_command": "cd packages/backend && poetry build"
       },
       {
         "name": "shared-utils",
         "path": "packages/shared",
         "type": "library",
         "config_file": "packages/shared/package.json",
         "test_command": "yarn workspace shared test"
       }
     ]
   }
   ```

4. **Use in operations:** When running tests/builds:
   - If monorepo: run per-subproject or use workspace commands
   - Example: `yarn workspace frontend test` not just `yarn test`
   - Allow targeting specific subprojects: `/pm:test --project=frontend`

**Success Criteria:**
- CCPM understands monorepo structure and doesn't try to run root-level commands
- Agents can target specific subprojects for testing/building
- Multi-project configuration stored and accessible

---

### Feature 6: CI/CD Toolchain Integration

**Goal:** Understand existing CI/CD system and avoid breaking it.

**Instructions for CCPM:**

Detect CI/CD system and understand existing workflows:

1. **Detect CI system:**
   - `.github/workflows/*.yml` exists → GitHub Actions
   - `.gitlab-ci.yml` exists → GitLab CI
   - `Jenkinsfile` exists → Jenkins
   - `.circleci/config.yml` exists → CircleCI
   - `.travis.yml` exists → Travis CI
   - `azure-pipelines.yml` exists → Azure Pipelines

2. **Parse workflow files** (GitHub Actions example):
   - Find all workflow files in `.github/workflows/`
   - For each workflow YAML:
     - Extract workflow name
     - Extract trigger conditions (`on: push`, `on: pull_request`, etc.)
     - Extract job names
     - Extract commands run in each job (from `run:` steps)
     - Extract required secrets (from `secrets.` references)
     - Extract environment variables
     - Note OS requirements (`runs-on: ubuntu-latest`)

3. **Store in `.claude/learned/ci-config.json`:**
   ```json
   {
     "system": "github-actions",
     "detected_at": "2025-11-13T12:00:00Z",
     "workflows": {
       "test.yml": {
         "name": "Test Suite",
         "file_path": ".github/workflows/test.yml",
         "triggers": ["push", "pull_request"],
         "jobs": {
           "test": {
             "runs_on": "ubuntu-latest",
             "steps": [
               "actions/checkout@v3",
               "Setup Node.js",
               "yarn install",
               "yarn test"
             ],
             "commands": {
               "test": "yarn test",
               "lint": "yarn lint"
             }
           }
         },
         "required_secrets": ["NPM_TOKEN"],
         "env_vars": ["NODE_VERSION"]
       },
       "build.yml": {
         "name": "Build & Deploy",
         "triggers": ["push"],
         "branches": ["main"],
         "jobs": {
           "build": {
             "commands": {
               "build": "yarn build",
               "deploy": "yarn deploy"
             }
           }
         }
       }
     },
     "primary_test_command": "yarn test",
     "primary_build_command": "yarn build",
     "runs_on_pr": true,
     "runs_on_push": true
   }
   ```

4. **Safety rules for agents:**
   - **NEVER modify CI workflow files** without explicit user approval
   - Before making code changes, note which CI jobs might be affected
   - When suggesting changes, warn: "This will trigger CI workflow: test.yml"
   - Before merging PRs, verify CI passes: `gh pr checks`
   - If adding new dependencies, note they might need CI updates

**Success Criteria:**
- CCPM understands existing CI and doesn't break workflows
- Agents aware of what commands CI runs (and match them locally)
- No accidental modifications to `.github/workflows/` files

---

## How to Invoke

```
/skill project-intelligence
```

Then CCPM will:
1. Scan project root for configuration files
2. Detect all tools and frameworks
3. Parse CI/CD workflows
4. Store learned configuration in `.claude/learned/`
5. Report summary of detected configuration

## Output Example

```
🧠 Project Intelligence Report

✅ Configuration Files Detected:
  - pyproject.toml (Python project with ruff, mypy, pytest)
  - package.json (Node.js project with yarn)
  - Makefile (6 targets: test, build, clean, lint, format, deploy)

✅ Package Manager: yarn (detected from yarn.lock)

✅ CLI Tools Available:
  - Test: yarn test (runs jest)
  - Build: yarn build (runs webpack)
  - Lint: yarn lint (runs eslint)
  - Format: yarn format (runs prettier)

✅ CI/CD System: GitHub Actions
  - test.yml: Runs on PR, executes yarn test + yarn lint
  - build.yml: Runs on push to main, builds and deploys

✅ Project Type: Monorepo (yarn workspaces)
  - 3 subprojects detected:
    - frontend (React app)
    - backend (FastAPI)
    - shared (TypeScript library)

📝 Configuration stored in:
  - .claude/learned/project-config.json
  - .claude/learned/cli-tools.json
  - .claude/learned/project-structure.json
  - .claude/learned/ci-config.json

✅ CCPM is now configured to respect your project's tools and settings!
```

## Files Created

This skill creates/updates:
- `.claude/learned/project-config.json` - Parsed tool configurations
- `.claude/learned/cli-tools.json` - Detected CLI commands
- `.claude/learned/project-structure.json` - Monorepo structure
- `.claude/learned/ci-config.json` - CI/CD workflow information

## Integration with Other CCPM Features

**Other agents/commands will read these files:**
- `/pm:test` reads `project-config.json` to know how to run tests
- `/pm:lint` reads `project-config.json` to know which linter to use
- `/pm:commit` reads `ci-config.json` to know what CI will run
- All agents read `cli-tools.json` to use correct package manager

**You don't need to manually configure anything** - just invoke this skill once and CCPM adapts to your project!

## When to Re-run

Re-run this skill when:
- You switch package managers (npm → yarn)
- You add new CI workflows
- You change tool configuration in pyproject.toml
- You restructure a monorepo (add/remove subprojects)
- After pulling major project changes from git

## Troubleshooting

**"No configuration files found"**
- This skill only works if your project has standard config files
- At minimum: `pyproject.toml`, `package.json`, or `Makefile`

**"CLI tools not detected correctly"**
- Check that lockfiles exist (yarn.lock, package-lock.json, etc.)
- Verify Makefile targets are properly formatted

**"Monorepo not detected"**
- Ensure `workspaces` field is in root `package.json`
- Or `pnpm-workspace.yaml` exists for pnpm
- Or multiple `pyproject.toml` in subdirectories

---

**Skill Version:** 1.0
**Last Updated:** 2025-11-13
**Status:** Active
**Implements:** Features 1, 2, 4, 6 from Intelligence Plan
