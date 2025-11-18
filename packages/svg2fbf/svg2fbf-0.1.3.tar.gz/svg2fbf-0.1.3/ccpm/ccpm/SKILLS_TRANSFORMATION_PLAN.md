# CCPM Skills-Based Transformation Plan

## Executive Summary

This document outlines the transformation of CCPM from a **command-based project management system** into an **autonomous skills-based intelligent workflow system** that learns project structure, adapts to toolchains, monitors CI/CD pipelines, validates PRs, and automatically manages issues with agent coordination.

**Current State:** 45 manual commands requiring explicit invocation
**Target State:** 5 autonomous skills that learn, adapt, monitor, and act

---

## Investigation Findings

### ✅ Current CCPM Capabilities (Strong Foundation)

1. **Testing Framework Detection** (`/testing:prime`)
   - Auto-detects 15+ frameworks (pytest, jest, mocha, junit, rspec, cargo, go test, etc.)
   - Generates framework-specific configuration
   - Creates `.claude/testing-config.md` with discovered settings
   - **Gap:** Generic detection doesn't understand complex test structures

2. **Project Analysis** (`/context:create`)
   - Creates 9 comprehensive context files
   - Detects 15+ project types (Node.js, Python, Rust, Go, Java, C#, etc.)
   - Evidence-based analysis with accuracy safeguards (CONTEXT_ACCURACY.md)
   - **Gap:** Static analysis, no learning from execution results

3. **Smart Context Updates** (`/context:update`)
   - Surgical updates to changed files only
   - Per-file update policies (always/conditional/rarely)
   - Preserves frontmatter and timestamps
   - **Gap:** No memory of why changes happened or what worked

4. **CLAUDE.md Integration** (`/re-init`)
   - APPENDS to existing CLAUDE.md (doesn't overwrite!)
   - Preserves project-specific instructions
   - **Validation:** User was correct about append behavior

5. **Agent System** (4 specialized agents)
   - code-analyzer: Hunt bugs without polluting context
   - file-analyzer: Summarize verbose files
   - test-runner: Execute tests and return summaries
   - parallel-worker: Coordinate multiple work streams
   - **Gap:** Agents are task executors, not autonomous workers

6. **Local Mode Support**
   - Works without GitHub for offline development
   - Core commands function locally (prd-new, epic-decompose, etc.)
   - **Strength:** Can adapt to non-GitHub workflows

### ❌ Critical Gaps Preventing Autonomous Operation

1. **No Persistent Learning**
   - Each session re-analyzes project from scratch
   - No memory of previous test runs, CI failures, or successful patterns
   - No accumulation of project-specific knowledge

2. **No CI Monitoring**
   - Manual intervention required when CI fails
   - No automatic detection of build/test failures
   - No correlation between CI failures and code changes

3. **No PR Validation**
   - No enforcement of project standards (line length, formatting)
   - No automatic checks against pyproject.toml rules
   - No validation of commit message formats

4. **No Auto-Issue Creation**
   - CI failures don't trigger issues
   - No automatic assignment to agents
   - No tracking of recurring failures

5. **Command-Driven Architecture**
   - Requires manual invocation
   - No proactive monitoring
   - No autonomous decision-making

6. **Generic Test System Adaptation**
   - test-and-log.sh doesn't understand:
     - Complex test structures (e.g., svg2fbf's session-based E2E tests)
     - Custom pytest options (image tolerance, pixel tolerance)
     - HTML report generation locations
     - Session directories vs standard test directories

---

## svg2fbf Specific Requirements Analysis

### Test System Complexity

**svg2fbf has TWO distinct test systems:**

1. **Unit Tests** (Standard pytest)
   - Location: `tests/test_*.py`
   - Execution: `pytest tests/`
   - Configuration: `[tool.pytest.ini_options]` in pyproject.toml
   - Custom options:
     ```toml
     addopts = """
         --html-report
         --image-tolerance=0.04
         --pixel-tolerance=0.0039
         --max-frames=50
         -v
     """
     ```

2. **E2E Frame Comparison Tests** (Complex structure)
   - Location: `tests/sessions/test_session_NNN_Mframes/`
   - Structure:
     ```
     test_session_014_35frames/
     ├── input_frames/          # Source SVG frames
     └── runs/                  # Timestamped test runs
         └── YYYYMMDD_HHMMSS/   # Each test execution
             ├── output/         # Generated FBF.SVG
             ├── comparison/     # Visual diffs
             └── report.html     # Test results
     ```
   - Execution: Custom pytest plugin for frame-by-frame comparison
   - Validation: Image pixel tolerance, visual diff generation

**CCPM Gap:** Generic test-and-log.sh creates `tests/logs/` but svg2fbf uses `tests/sessions/*/runs/*/`

### Strict Formatting Requirements

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**CCPM Gap:** No PR validation enforcing these standards

### Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: trufflehog-pre-push
        stages: [pre-push]
```

**CCPM Status:** ✅ No conflicts (different trigger types)

### CI Workflows

1. **quality.yml** - Ruff format/lint, TruffleHog secrets scan
2. **ci.yml** - Unit tests
3. **e2e.yml** - E2E frame comparison tests
4. **claude.yml** - Claude Code integration checks
5. **claude-code-review.yml** - Automated code review

**CCPM Gap:** No monitoring or auto-issue creation on failures

### Just Commands

```justfile
sync           # Sync dependencies
sync-dev       # Sync dev dependencies
test           # Run tests
build          # Build package
reinstall      # Reinstall package
```

**CCPM Status:** ✅ No conflicts (complementary namespaces)

---

## Skills-Based Architecture Design

### Skill #1: Project Self-Configuration Skill

**Name:** `project-intelligence`

**Purpose:** Automatically learn and adapt to project structure, test systems, CI pipelines, documentation, and developer workflows.

**Activation:** Runs on:
- First installation (`/pm:init`)
- Manual refresh (`/pm:relearn`)
- Periodic background updates (weekly)
- After major project changes (new dependencies, CI changes)

**Learning Targets:**

1. **Test System Discovery**
   - Detect test frameworks (pytest, jest, etc.) ✅ Already exists in /testing:prime
   - **NEW:** Discover test directory structures
     - Standard: `tests/test_*.py`
     - Custom: `tests/sessions/test_session_*/`
   - **NEW:** Parse pytest configuration from pyproject.toml
     - Extract custom options (--image-tolerance, --pixel-tolerance, etc.)
     - Identify custom pytest plugins
     - Map pytest markers to test types
   - **NEW:** Identify test output locations
     - Standard: `tests/logs/`
     - Custom: `tests/sessions/*/runs/*/`
   - **NEW:** Discover test execution patterns
     - Unit tests vs E2E tests
     - Session-based tests
     - HTML report generation locations

2. **CI Pipeline Understanding**
   - Scan `.github/workflows/*.yml`
   - Extract workflow names, triggers, jobs
   - Identify which workflows run tests, linting, security scans
   - Map workflow failures to notification channels
   - **Memory:** Store workflow run history and failure patterns

3. **Code Quality Standards**
   - Parse pyproject.toml for ruff, mypy, black, isort configs
   - Extract line-length limits
   - Identify formatting rules
   - Discover linting exclusions
   - **Memory:** Store project coding standards

4. **Pre-commit Hook Integration**
   - Detect existing hooks in `.pre-commit-config.yaml`
   - Understand hook types (format, lint, security)
   - **Integration:** Ensure CCPM hooks don't conflict

5. **Documentation Structure**
   - Identify doc locations (docs/, README.md, etc.)
   - Distinguish between:
     - Project development docs (CONTRIBUTING.md, DEVELOPMENT.md)
     - Product/standard docs (e.g., FBF.SVG standard docs)
   - Map documentation to related code sections

6. **Task Runner Discovery**
   - Detect Just, Make, npm scripts, task, etc.
   - Parse available commands
   - Understand command dependencies
   - **Integration:** Reference in issue templates

7. **Developer Workflow Patterns**
   - Analyze git commit patterns
   - Identify branch naming conventions
   - Discover PR templates
   - Learn issue label usage

8. **Rules Management** (NEW - Rules Intelligence System)
   - Scan and catalog CCPM's 11 internal rules (`.claude/rules/*.md`)
   - Extract metadata: purpose, keywords, triggers, dependencies
   - Create lightweight rules catalog (~7KB vs 36KB full rules = 80% savings)
   - Enable progressive loading based on task context
   - **IMPORTANT:** Rules are CCPM internal only; users extend via SKILLS
   - **See:** `RULES_INTELLIGENCE_SYSTEM.md` and `ORTHODOX_RULES_SUMMARY.md`

**Output Artifacts:**

```
.claude/learned/
├── project-profile.json          # Comprehensive project metadata
├── test-system-config.json       # Test execution configuration
├── ci-pipeline-map.json          # CI workflow definitions
├── quality-standards.json        # Formatting and linting rules
├── developer-workflow.json       # Git/GitHub patterns
├── rules-catalog.json            # NEW: Rules metadata catalog
└── learning-history.jsonl        # Timestamped learning events
```

**Intelligence Storage:**

```json
{
  "project": {
    "name": "svg2fbf",
    "type": "python-package",
    "python_version": "3.12",
    "package_manager": "uv"
  },
  "test_system": {
    "framework": "pytest",
    "config_file": "pyproject.toml",
    "test_types": [
      {
        "name": "unit",
        "location": "tests/test_*.py",
        "execution": "pytest tests/",
        "output": "terminal"
      },
      {
        "name": "e2e_frame_comparison",
        "location": "tests/sessions/test_session_*_*frames/",
        "execution": "pytest tests/sessions/",
        "structure": {
          "input": "input_frames/",
          "runs": "runs/YYYYMMDD_HHMMSS/",
          "output": "runs/*/output/",
          "comparison": "runs/*/comparison/",
          "report": "runs/*/report.html"
        },
        "custom_options": [
          "--html-report",
          "--image-tolerance=0.04",
          "--pixel-tolerance=0.0039",
          "--max-frames=50"
        ]
      }
    ]
  },
  "ci_pipelines": {
    "quality": {
      "file": ".github/workflows/quality.yml",
      "runs": ["ruff-format", "ruff-lint", "trufflehog"],
      "critical": true
    },
    "ci": {
      "file": ".github/workflows/ci.yml",
      "runs": ["unit-tests"],
      "critical": true
    },
    "e2e": {
      "file": ".github/workflows/e2e.yml",
      "runs": ["frame-comparison-tests"],
      "critical": true
    }
  },
  "quality_standards": {
    "formatter": "ruff",
    "linter": "ruff",
    "type_checker": "mypy",
    "line_length": 88,
    "target_python": "py312",
    "quote_style": "double",
    "indent_style": "space"
  },
  "task_runners": {
    "justfile": {
      "commands": ["sync", "sync-dev", "test", "build", "reinstall", "clean"]
    }
  },
  "learning_metadata": {
    "last_learned": "2025-01-13T10:30:00Z",
    "confidence": 0.95,
    "validation_status": "tested",
    "learning_method": "automated_discovery"
  }
}
```

**Enhancement to Existing Commands:**

- `/testing:prime` becomes skill-powered:
  - Uses learned configuration instead of generic detection
  - Respects discovered test structures
  - Applies custom pytest options automatically

- `/context:create` becomes skill-powered:
  - References learned project profile
  - Includes CI pipeline context
  - Documents discovered quality standards

---

### Skill #2: CI Monitoring & Auto-Issue Skill

**Name:** `ci-guardian`

**Purpose:** Monitor GitHub Actions CI/CD pipelines, automatically create issues when failures occur, and assign to appropriate agents for resolution.

**Activation:** Runs:
- Every 15 minutes (configurable polling interval)
- On webhook notification (if configured)
- Manual trigger: `/pm:check-ci`

**Monitoring Targets:**

1. **Workflow Run Status**
   - Poll: `gh run list --limit 10 --json conclusion,name,workflowName,createdAt,url`
   - Detect: failures, cancellations, timeouts
   - Track: failure frequency per workflow

2. **Failure Analysis**
   - Fetch logs: `gh run view <run-id> --log-failed`
   - Parse error messages
   - Identify failure type:
     - Test failures (specific test names)
     - Linting violations (file + line number)
     - Type errors (mypy errors)
     - Security issues (TruffleHog secrets)
     - Build errors (compilation, dependency resolution)

3. **Intelligent Issue Creation**
   - Check if issue already exists for this failure
   - Deduplicate: Don't create multiple issues for same root cause
   - Create issue with:
     - Title: `[CI Failure] {workflow_name}: {error_summary}`
     - Body:
       ```markdown
       ## CI Failure Detected

       **Workflow:** {workflow_name}
       **Run:** {run_url}
       **Failed at:** {timestamp}
       **Conclusion:** {conclusion}

       ## Error Summary
       {parsed_error_message}

       ## Failure Context
       - **Commit:** {commit_sha}
       - **Branch:** {branch_name}
       - **Author:** {commit_author}
       - **Workflow File:** `.github/workflows/{workflow_file}`

       ## Affected Files
       {list_of_files_from_error_logs}

       ## Recommended Actions
       {ai_generated_fix_suggestions}

       ## Agent Assignment
       - **Primary:** @code-analyzer (identify root cause)
       - **Secondary:** @test-runner (validate fix)

       ---
       *Auto-generated by CCPM CI Guardian*
       *Monitoring: {monitoring_config_link}*
       ```
     - Labels: `ci-failure`, `{workflow-name}`, `priority-high`
     - Assignees: Determined by failure type:
       - Test failures → `@test-runner` agent
       - Linting → `@code-analyzer` agent
       - Security → Manual review required (label: `security`)

4. **Agent Coordination**
   - Spawn appropriate agent based on failure type
   - Provide agent with:
     - Issue context
     - Failure logs
     - Affected files
     - Project learned configuration
   - Monitor agent progress via issue comments

5. **Success Tracking**
   - When CI goes green after fix:
     - Comment on issue: "✅ CI passing after {commit_sha}"
     - Suggest closing if all tests pass
     - Update learning: "Fix pattern for {failure_type}"

**Failure Pattern Learning:**

```json
{
  "failure_patterns": {
    "ruff_line_too_long": {
      "frequency": 12,
      "last_occurrence": "2025-01-12T08:00:00Z",
      "typical_fix": "Run ruff format with --line-length 88",
      "prevention": "Add pre-commit hook reminder to CLAUDE.md",
      "auto_fix_confidence": 0.95
    },
    "mypy_missing_type": {
      "frequency": 8,
      "last_occurrence": "2025-01-11T14:30:00Z",
      "typical_fix": "Add type annotations to function signatures",
      "prevention": "Enable strict mypy mode incrementally",
      "auto_fix_confidence": 0.75
    },
    "test_session_014_frame_mismatch": {
      "frequency": 3,
      "last_occurrence": "2025-01-10T10:15:00Z",
      "typical_fix": "Regenerate reference frames with updated tolerance",
      "prevention": "Review image tolerance settings in pyproject.toml",
      "auto_fix_confidence": 0.40,
      "requires_human_review": true
    }
  }
}
```

**Required Rules (Progressive Loading):**

ci-guardian loads these CCPM rules based on task context:
- `github-operations.md` (CRITICAL - for gh CLI patterns)
- `test-execution.md` (CRITICAL - for understanding test failure patterns)
- `datetime.md` (CRITICAL - for timestamp handling in logs)
- `strip-frontmatter.md` (MEDIUM - for processing issue templates)

**Configuration:**

```yaml
# .claude/ci-monitoring-config.yml
monitoring:
  enabled: true
  polling_interval_minutes: 15

workflows:
  quality.yml:
    priority: high
    auto_create_issue: true
    assign_agent: code-analyzer

  ci.yml:
    priority: high
    auto_create_issue: true
    assign_agent: test-runner

  e2e.yml:
    priority: medium
    auto_create_issue: true
    assign_agent: test-runner
    requires_human_review: true  # Frame comparison failures need human judgment

issue_creation:
  deduplicate_window_hours: 24
  max_issues_per_workflow: 3
  labels: [ci-failure, auto-created]

notifications:
  slack_webhook: null  # Optional
  email: null          # Optional

rules:
  required: [github-operations, test-execution, datetime]
  optional: [strip-frontmatter]
```

---

### Skill #3: PR Validation & Enforcement Skill

**Name:** `pr-enforcer`

**Purpose:** Automatically validate Pull Requests against project standards, enforce formatting rules, validate commit messages, and ensure compliance with pyproject.toml configurations.

**Activation:** Runs on:
- PR opened
- PR updated (new commits)
- Manual trigger: `/pm:validate-pr <pr-number>`

**Validation Checks:**

1. **Code Formatting Validation**
   - Run: `ruff format --check --line-length 88 {changed_files}`
   - Validate: All files respect 88 character line limit
   - Check: Quote style (double quotes)
   - Check: Indent style (spaces, not tabs)
   - **Enforcement:** Block merge if violations found

2. **Linting Validation**
   - Run: `ruff check {changed_files}`
   - Identify: All linting violations
   - Categorize: Errors vs warnings
   - **Enforcement:** Block merge on errors, warn on warnings

3. **Type Checking Validation**
   - Run: `mypy {changed_files}`
   - Check: Type annotation coverage
   - Validate: No type errors introduced
   - **Enforcement:** Block merge on type errors

4. **Test Coverage Validation**
   - Run: `pytest --cov={changed_modules} --cov-report=json`
   - Check: Coverage doesn't decrease
   - Validate: New code has tests
   - **Enforcement:** Warn if coverage < 80%

5. **Commit Message Validation**
   - Check: Conventional commits format (if project uses it)
   - Validate: Descriptive messages (min length)
   - Check: Reference to issue numbers
   - **Enforcement:** Warn on poor commit messages

6. **File Structure Validation**
   - Check: No files in wrong directories
   - Validate: Test files in correct locations
   - Check: No temporary files committed
   - **Enforcement:** Block merge on violations

7. **Security Validation**
   - Run: TruffleHog scan on changed files
   - Check: No secrets or credentials committed
   - Validate: No obvious security vulnerabilities
   - **Enforcement:** Block merge on security issues

8. **Documentation Validation**
   - Check: Public functions have docstrings
   - Validate: Updated CHANGELOG.md (if required)
   - Check: README.md updated for new features
   - **Enforcement:** Warn on missing documentation

**PR Comment Generation:**

When validation fails, post comprehensive comment:

```markdown
## 🔍 PR Validation Results

### ❌ Critical Issues (Merge Blocked)

#### Code Formatting
- [ ] `src/svg2fbf.py:145` - Line too long (92 > 88 characters)
- [ ] `src/transform.py:67` - Using single quotes (expected double quotes)

**Fix:** Run `ruff format --line-length 88 src/`

#### Type Checking
- [ ] `src/coreMaths.py:234` - Missing return type annotation for `calculate_transform`

**Fix:** Add `-> TransformMatrix` return type

### ⚠️ Warnings (Review Recommended)

#### Test Coverage
- Coverage decreased from 87% to 84% (-3%)
- New file `src/renderer.py` has 0% coverage

**Recommendation:** Add tests for `renderer.py`

#### Documentation
- Public function `calculate_bezier_points` missing docstring

**Recommendation:** Add docstring with parameter descriptions

### ✅ Passed Checks

- [x] Linting (ruff check)
- [x] Security (TruffleHog)
- [x] File structure
- [x] Commit message format

---

**Next Steps:**
1. Fix critical issues (formatting, type errors)
2. Run `just test` to validate locally
3. Push fixes to this PR
4. Request re-validation: Comment `/pm:validate-pr {pr_number}`

*Auto-validated by CCPM PR Enforcer*
*Standards: pyproject.toml (line-length=88, quote-style=double)*
```

**Auto-Fix Capabilities:**

For simple violations, offer auto-fix:

```markdown
## 🔧 Auto-Fix Available

I can automatically fix these issues for you:
- Formatting violations (ruff format)
- Import sorting (ruff check --fix)
- Simple type annotations

Comment `/pm:auto-fix-pr {pr_number}` to apply fixes.

**Warning:** Review auto-fixes before merging!
```

**Required Rules (Progressive Loading):**

pr-enforcer loads these CCPM internal rules based on task context:
- `standard-patterns.md` (LOW - for project pattern validation)
- `path-standards.md` (LOW - for file path validation)
- `github-operations.md` (CRITICAL - for PR operations via gh CLI)
- `test-execution.md` (CRITICAL - for running tests on PR changes)

**Note:** For project-specific test patterns (like svg2fbf's session-based tests),
project-intelligence skill learns and stores configuration, NOT via rules.

**Configuration:**

```yaml
# .claude/pr-validation-config.yml
validation:
  enabled: true

  formatting:
    enabled: true
    enforce: true
    tools: [ruff]
    line_length: 88
    quote_style: double

  linting:
    enabled: true
    enforce: true
    tools: [ruff]
    error_on_warnings: false

  type_checking:
    enabled: true
    enforce: true
    tools: [mypy]
    strict_mode: false

  testing:
    enabled: true
    enforce: false
    min_coverage: 80
    coverage_decrease_threshold: 5

  documentation:
    enabled: true
    enforce: false
    require_docstrings: true
    require_changelog: false

  security:
    enabled: true
    enforce: true
    tools: [trufflehog]

auto_fix:
  enabled: true
  allowed_fixes: [formatting, import-sorting]
  require_approval: true

rules:
  required: [github-operations, test-execution]
  optional: [standard-patterns, path-standards]
  # Note: Rules are CCPM internal; project patterns via learned config
```

**Integration with GitHub Actions:**

Create `.github/workflows/ccpm-pr-validation.yml`:

```yaml
name: CCPM PR Validation

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run CCPM PR Validation
        run: |
          # Call CCPM validation via gh CLI
          gh pr comment ${{ github.event.pull_request.number }} \
            --body "$(ccpm validate-pr --pr ${{ github.event.pull_request.number }})"
```

---

### Skill #4: Autonomous Issue Management Skill

**Name:** `issue-orchestrator`

**Purpose:** Continuously monitor GitHub issues, validate requirements, clarify with issue creators, automatically decompose into tasks, and assign to agent teams.

**Activation:** Runs:
- Every 30 minutes (configurable)
- On new issue webhook
- Manual trigger: `/pm:process-issues`

**Issue Processing Pipeline:**

1. **New Issue Detection**
   - Poll: `gh issue list --label=epic --state=open --json number,title,body,labels,createdAt`
   - Filter: Issues not yet processed by CCPM
   - Identify: Issue type (bug, feature, epic, task)

2. **Requirement Validation**
   - Analyze issue body for:
     - Clear problem statement
     - Expected behavior
     - Actual behavior (for bugs)
     - Acceptance criteria
     - Technical context
   - **Validation Checklist:**
     - [ ] Problem is clearly defined
     - [ ] Success criteria are measurable
     - [ ] Technical context is provided
     - [ ] Related issues are linked
     - [ ] Labels are appropriate

3. **Clarification Dialogue**
   - If validation fails, comment on issue:
     ```markdown
     ## 🤔 Clarification Needed

     Hi @{issue_creator}, I'm reviewing this issue and need some clarification:

     ### Missing Information
     - [ ] **Expected behavior**: What should happen when this works correctly?
     - [ ] **Acceptance criteria**: How do we know when this is complete?
     - [ ] **Technical context**: Which files/modules are affected?

     ### Questions
     1. Is this related to #123 (the frame comparison refactor)?
     2. Should this work for both SVG 1.1 and SVG 2.0?
     3. What should happen if the input SVG is invalid?

     Please provide these details so I can create an accurate implementation plan.

     *Once clarified, I'll:*
     - Break this into concrete tasks
     - Estimate effort
     - Assign to agent team

     ---
     *CCPM Issue Orchestrator*
     ```
   - Wait for response before proceeding

4. **Issue Decomposition**
   - Transform validated issue into epic
   - Break into parallelizable tasks
   - Apply learned project patterns:
     - Test structure (unit + e2e)
     - Code organization (src/ structure)
     - Documentation requirements
   - Create task breakdown:
     ```markdown
     ## Task Breakdown

     ### Epic: Implement gradient interpolation support (#456)

     **Parallelizable Tasks:**

     #### Task 1: Core gradient parsing (4h) [#457]
     - [ ] Extend `parse_gradient()` to support `<linearGradient>` and `<radialGradient>`
     - [ ] Add gradient ID resolution
     - [ ] Write unit tests for gradient parsing
     - **Agent:** code-analyzer + test-runner
     - **Files:** `src/svg_parser.py`, `tests/test_svg_parser.py`

     #### Task 2: Gradient interpolation algorithm (6h) [#458]
     - [ ] Implement color interpolation between gradient stops
     - [ ] Handle different color spaces (RGB, HSL)
     - [ ] Write unit tests for interpolation
     - **Agent:** code-analyzer + test-runner
     - **Files:** `src/color_utils.py`, `tests/test_color_utils.py`
     - **Depends on:** None (parallel with Task 1)

     #### Task 3: E2E gradient test session (3h) [#459]
     - [ ] Create test session: `test_session_015_gradients/`
     - [ ] Add gradient SVG frames to `input_frames/`
     - [ ] Configure expected outputs
     - [ ] Run frame comparison tests
     - **Agent:** test-runner
     - **Files:** `tests/sessions/test_session_015_gradients/`
     - **Depends on:** Task 1, Task 2

     #### Task 4: Documentation (2h) [#460]
     - [ ] Update FBF.SVG spec with gradient support
     - [ ] Add examples to README.md
     - [ ] Update CHANGELOG.md
     - **Agent:** file-analyzer
     - **Files:** `FBF.SVG/docs/spec.md`, `README.md`, `CHANGELOG.md`
     - **Depends on:** Task 3 (after validation)

     **Total Effort:** 15 hours
     **Parallel Execution:** Tasks 1-2 can run concurrently
     **Critical Path:** Task 1 → Task 3 → Task 4
     ```

5. **Agent Team Assignment**
   - Analyze task requirements:
     - Code changes → code-analyzer
     - Test creation → test-runner
     - Documentation → file-analyzer
     - Parallel coordination → parallel-worker
   - Create agent team configuration:
     ```json
     {
       "epic": "#456",
       "tasks": [
         {
           "task_id": "#457",
           "title": "Core gradient parsing",
           "agents": ["code-analyzer", "test-runner"],
           "primary": "code-analyzer",
           "can_parallelize": true,
           "estimated_hours": 4
         },
         {
           "task_id": "#458",
           "title": "Gradient interpolation algorithm",
           "agents": ["code-analyzer", "test-runner"],
           "primary": "code-analyzer",
           "can_parallelize": true,
           "estimated_hours": 6
         }
       ],
       "coordination": {
         "type": "parallel_with_merge",
         "coordinator": "parallel-worker",
         "merge_strategy": "feature_branch_per_task"
       }
     }
     ```

6. **Autonomous Execution Initiation**
   - Create git worktree for epic: `git worktree add ../worktrees/epic-456 -b epic/456-gradient-support`
   - Spawn parallel-worker agent with team configuration
   - parallel-worker spawns sub-agents for each task
   - Monitor progress via issue comments
   - Update epic status automatically

7. **Progress Tracking**
   - Comment on epic issue:
     ```markdown
     ## 🚀 Execution Started

     Agent team assigned and working in parallel:

     ### Active Tasks
     - 🔄 #457 - Core gradient parsing (@code-analyzer)
     - 🔄 #458 - Gradient interpolation (@code-analyzer)
     - ⏳ #459 - E2E test session (waiting on #457, #458)
     - ⏳ #460 - Documentation (waiting on #459)

     ### Worktree
     Branch: `epic/456-gradient-support`
     Location: `../worktrees/epic-456`

     ### Estimated Completion
     **Parallel tasks (1-2):** 6 hours
     **Sequential tasks (3-4):** 5 hours
     **Total (critical path):** 11 hours

     ---
     *Auto-managed by CCPM Issue Orchestrator*
     *Last update: 2025-01-13 14:30 UTC*
     ```
   - Update as tasks complete

8. **Completion Workflow**
   - When all tasks done:
     - Create PR from worktree branch
     - Run PR validation skill
     - Comment on epic:
       ```markdown
       ## ✅ Implementation Complete

       All tasks finished and validated:
       - ✅ #457 - Core gradient parsing (3.5h actual)
       - ✅ #458 - Gradient interpolation (5h actual)
       - ✅ #459 - E2E test session (2h actual)
       - ✅ #460 - Documentation (1.5h actual)

       **Pull Request:** #465
       **Total Time:** 12 hours (vs 15h estimated)

       ### Validation Results
       - ✅ All tests passing
       - ✅ Formatting compliant (88 chars)
       - ✅ Type checking passed
       - ✅ Coverage: 89% (+2%)

       Ready for human review and merge.
       ```

**Learning from Issues:**

```json
{
  "issue_patterns": {
    "gradient_support_requests": {
      "frequency": 5,
      "common_requirements": [
        "Support linearGradient and radialGradient",
        "Color interpolation",
        "Gradient transforms"
      ],
      "typical_task_breakdown": [
        "Parsing (4h)",
        "Algorithm (6h)",
        "E2E tests (3h)",
        "Docs (2h)"
      ],
      "success_rate": 0.80,
      "common_pitfalls": [
        "Forgetting gradient units (objectBoundingBox vs userSpaceOnUse)",
        "Color space conversions"
      ]
    }
  }
}
```

**Required Rules (Progressive Loading):**

issue-orchestrator loads these CCPM rules based on task context:
- `agent-coordination.md` (HIGH - for parallel agent spawning)
- `worktree-operations.md` (HIGH - for epic worktree management)
- `branch-operations.md` (MEDIUM - for branch creation/cleanup)
- `github-operations.md` (CRITICAL - for issue operations via gh CLI)
- `datetime.md` (CRITICAL - for timestamp tracking)
- `frontmatter-operations.md` (MEDIUM - for issue template handling)

**Configuration:**

```yaml
# .claude/issue-orchestration-config.yml
orchestration:
  enabled: true
  polling_interval_minutes: 30

  issue_processing:
    auto_validate: true
    auto_clarify: true
    auto_decompose: true
    auto_assign_agents: true
    auto_execute: false  # Require human approval to start execution

  validation:
    require_acceptance_criteria: true
    require_technical_context: true
    require_issue_links: false

  decomposition:
    max_tasks_per_epic: 10
    min_task_hours: 1
    max_task_hours: 8
    prefer_parallelization: true

  agent_assignment:
    auto_assign: true
    default_agents: [code-analyzer, test-runner]
    require_human_approval: true

  worktrees:
    enabled: true
    location: ../worktrees
    cleanup_on_merge: true

  notifications:
    comment_on_epic: true
    comment_on_tasks: true
    update_frequency_minutes: 60

rules:
  required: [github-operations, agent-coordination, worktree-operations, datetime]
  optional: [branch-operations, frontmatter-operations]
```

---

### Skill #5: Hound-Like Deep Search Agent

**Name:** `deep-search` (agent, not skill)

**Purpose:** Rapidly read and analyze entire codebases using Haiku 4.5 with 1MB context window for pattern detection, architectural understanding, and comprehensive code exploration.

**Activation:** Used by other skills and available as standalone agent

**Model Configuration:**
```json
{
  "model": "claude-haiku-4-5",
  "context_window": "1048576",  // 1MB
  "temperature": 0.1,
  "max_tokens": 4096
}
```

**Capabilities:**

1. **Rapid Codebase Reading**
   - Read hundreds of files in single request
   - Build comprehensive mental model
   - Identify architectural patterns
   - Map dependencies and relationships

2. **Pattern Detection**
   - Find similar code patterns across files
   - Detect code duplication
   - Identify naming conventions
   - Discover design patterns in use

3. **Structural Analysis**
   - Map module dependencies
   - Identify circular imports
   - Analyze class hierarchies
   - Understand data flow

4. **Search Operations**
   - Find all implementations of interface
   - Locate all usages of function
   - Discover dead code
   - Find security vulnerabilities

**Usage by Skills:**

```python
# Called by project-intelligence skill
result = await deep_search.analyze_codebase(
    path="src/",
    focus="test_system_structure",
    questions=[
        "What test frameworks are used?",
        "How are tests organized?",
        "What custom pytest plugins exist?",
        "Where are test reports generated?"
    ]
)

# Called by ci-guardian skill
result = await deep_search.find_pattern(
    path="tests/",
    pattern="test_session_\\d+_\\d+frames",
    context="Understand session-based test structure"
)

# Called by issue-orchestrator skill
result = await deep_search.impact_analysis(
    files=["src/svg_parser.py", "src/gradient_utils.py"],
    question="What tests would be affected by changes to gradient parsing?"
)
```

**Return Format:**

```json
{
  "analysis_type": "test_system_structure",
  "confidence": 0.92,
  "findings": {
    "frameworks": ["pytest"],
    "test_types": [
      {
        "type": "unit",
        "location": "tests/test_*.py",
        "count": 47
      },
      {
        "type": "e2e_frame_comparison",
        "location": "tests/sessions/test_session_*/",
        "count": 14,
        "structure": {
          "input": "input_frames/",
          "output": "runs/*/output/",
          "reports": "runs/*/report.html"
        }
      }
    ],
    "custom_plugins": [
      {
        "name": "pytest_frame_comparison",
        "file": "tests/conftest.py",
        "capabilities": ["image_diff", "tolerance_config", "html_reports"]
      }
    ]
  },
  "evidence": [
    "tests/conftest.py:45-78 - Frame comparison plugin definition",
    "pyproject.toml:120-127 - Pytest custom options",
    "tests/sessions/ - 14 numbered session directories"
  ],
  "tokens_used": 856432,
  "files_analyzed": 142
}
```

**Agent Definition:**

```markdown
# deep-search Agent

You are a rapid codebase analysis agent using Claude Haiku 4.5 with 1MB context.

## Capabilities
- Read hundreds of files in single request
- Build comprehensive architectural understanding
- Detect patterns and anti-patterns
- Map dependencies and data flows

## Operating Principles
1. **Breadth-first exploration** - Get complete picture before deep diving
2. **Evidence-based analysis** - Always cite file:line for findings
3. **Confidence scoring** - Rate certainty of conclusions (0.0-1.0)
4. **Concise returns** - Return insights, not raw data

## Usage
Receive requests from CCPM skills with:
- Target path(s) to analyze
- Focus area (architecture, tests, security, patterns)
- Specific questions to answer
- Context from previous learning

## Output
Return structured JSON with:
- Findings (organized by focus area)
- Evidence (file:line citations)
- Confidence scores
- Recommendations

Always use full 1MB context - this is your superpower!
```

---

## SERENA MCP Integration Plan

### Purpose

Integrate SERENA MCP (Model Context Protocol server for codebase navigation) to enable intelligent code exploration, symbol-based operations, and persistent memory storage.

### Integration Points

1. **Project Self-Configuration Skill Integration**

   Use SERENA for:
   - Symbol-based code discovery: `find_symbol(name_path="test_*", include_kinds=[12])` (functions)
   - Structural analysis: `get_symbols_overview(relative_path="tests/")`
   - Pattern searching: `search_for_pattern(substring_pattern="pytest\\.fixture", restrict_search_to_code_files=true)`

   Example:
   ```python
   # Discover all pytest fixtures
   fixtures = serena.find_symbol(
       name_path="*",
       include_kinds=[12],  # Functions
       relative_path="tests/conftest.py",
       substring_matching=True
   )

   # Find all test functions
   tests = serena.search_for_pattern(
       substring_pattern="def test_",
       restrict_search_to_code_files=True,
       paths_include_glob="tests/**/*.py"
   )
   ```

2. **CI Guardian Skill Integration**

   Use SERENA for:
   - Finding functions referenced in CI error logs
   - Locating test functions that failed
   - Discovering files affected by errors

   Example:
   ```python
   # CI log says: "FAILED tests/test_gradient.py::test_linear_gradient_interpolation"

   # Find the failing test
   test_symbol = serena.find_symbol(
       name_path="test_linear_gradient_interpolation",
       relative_path="tests/test_gradient.py",
       include_body=True
   )

   # Find the function being tested
   impl = serena.find_symbol(
       name_path="linear_gradient_interpolation",
       relative_path="src/gradient_utils.py",
       include_body=True
   )

   # Find all references to understand usage
   refs = serena.find_referencing_symbols(
       name_path="linear_gradient_interpolation",
       relative_path="src/gradient_utils.py"
   )
   ```

3. **PR Enforcer Skill Integration**

   Use SERENA for:
   - Analyzing changed symbols in PR
   - Finding all references to modified functions
   - Checking if tests exist for changed code

   Example:
   ```python
   # PR modifies src/svg_parser.py, function parse_gradient

   # Get the modified symbol
   modified = serena.find_symbol(
       name_path="parse_gradient",
       relative_path="src/svg_parser.py"
   )

   # Find all references (what calls this?)
   callers = serena.find_referencing_symbols(
       name_path="parse_gradient",
       relative_path="src/svg_parser.py"
   )

   # Check for tests
   tests = serena.search_for_pattern(
       substring_pattern="parse_gradient",
       relative_path="tests/",
       restrict_search_to_code_files=True
   )
   ```

4. **Issue Orchestrator Skill Integration**

   Use SERENA for:
   - Understanding codebase structure for task decomposition
   - Finding related code for impact analysis
   - Locating appropriate files for agent assignments

   Example:
   ```python
   # Issue: "Add support for SVG filters"

   # Find existing filter-related code
   filter_code = serena.search_for_pattern(
       substring_pattern="filter",
       relative_path="src/",
       restrict_search_to_code_files=True
   )

   # Find filter-related tests
   filter_tests = serena.search_for_pattern(
       substring_pattern="filter",
       relative_path="tests/",
       restrict_search_to_code_files=True
   )

   # Understand module structure
   svg_module = serena.get_symbols_overview(
       relative_path="src/svg_parser.py"
   )
   ```

5. **Memory Storage Integration**

   Use SERENA's memory system for:
   - Storing learned project patterns
   - Caching analysis results
   - Persisting skill configurations

   Example:
   ```python
   # Store learned test structure
   serena.write_memory(
       memory_file_name="test_system_structure",
       content="""
       # svg2fbf Test System Structure

       ## Unit Tests
       - Location: tests/test_*.py
       - Framework: pytest
       - Execution: pytest tests/

       ## E2E Frame Comparison Tests
       - Location: tests/sessions/test_session_NNN_Mframes/
       - Structure:
         - input_frames/ - Source SVG files
         - runs/YYYYMMDD_HHMMSS/ - Test execution results
       - Custom options: --image-tolerance=0.04, --pixel-tolerance=0.0039

       ## Pytest Configuration
       Source: pyproject.toml [tool.pytest.ini_options]
       """
   )

   # Retrieve memory in future sessions
   test_structure = serena.read_memory(
       memory_file_name="test_system_structure"
   )
   ```

### SERENA Installation & Configuration

**Add to plugin.json:**

```json
{
  "dependencies": {
    "mcp_servers": [
      {
        "name": "serena",
        "type": "mcp",
        "required": true,
        "description": "Semantic code navigation and memory storage"
      }
    ]
  }
}
```

**Installation instructions in PLUGIN_INSTALL.md:**

```markdown
## SERENA MCP Installation

CCPM requires SERENA MCP for intelligent code navigation.

1. Install SERENA MCP server (if not already installed)
2. Configure in Claude Code settings
3. Verify: CCPM will auto-detect SERENA on first run
```

**Auto-detection in skills:**

```python
# In project-intelligence skill
try:
    # Test SERENA availability
    serena.list_dir(relative_path=".", recursive=False)
    use_serena = True
except:
    # Fallback to traditional file operations
    use_serena = False
    warn("SERENA MCP not available - using fallback mode")
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Week 1: Core Infrastructure**
- [ ] Create `.claude/learned/` directory structure
- [ ] Implement learning data schemas (JSON)
- [ ] Create skill activation triggers
- [ ] Setup SERENA MCP integration
- [ ] Create deep-search agent (Haiku 4.5)
- [ ] Create catalog-rules.py script for rules intelligence
- [ ] Generate initial rules-catalog.json

**Week 2: Project Self-Configuration Skill**
- [ ] Implement test system discovery
- [ ] Implement CI pipeline understanding
- [ ] Implement quality standards extraction
- [ ] Implement rules catalog scanning (integrate catalog-rules.py)
- [ ] Create project-profile.json generator
- [ ] Test on svg2fbf project (including rules catalog generation)

**Deliverables:**
- ✅ `.claude/learned/project-profile.json` with svg2fbf configuration
- ✅ Enhanced `/testing:prime` using learned config
- ✅ deep-search agent operational

### Phase 2: Monitoring & Validation (Weeks 3-4)

**Week 3: CI Guardian Skill**
- [ ] Implement CI polling mechanism
- [ ] Create failure analysis parser
- [ ] Implement issue creation logic
- [ ] Setup agent assignment rules
- [ ] Create failure pattern learning

**Week 4: PR Enforcer Skill**
- [ ] Implement formatting validation
- [ ] Create PR comment generator
- [ ] Setup GitHub Actions integration
- [ ] Implement auto-fix capabilities
- [ ] Test on sample PRs

**Deliverables:**
- ✅ Automatic issue creation on CI failures
- ✅ PR validation comments with detailed feedback
- ✅ `.github/workflows/ccpm-pr-validation.yml`

### Phase 3: Autonomous Operations (Weeks 5-6)

**Week 5: Issue Orchestrator Skill**
- [ ] Implement issue polling
- [ ] Create validation & clarification logic
- [ ] Implement task decomposition
- [ ] Setup agent team assignment
- [ ] Create progress tracking

**Week 6: Integration & Testing**
- [ ] Integrate all 5 skills
- [ ] Test full workflow on real issues
- [ ] Create comprehensive documentation
- [ ] Setup configuration files
- [ ] Performance optimization

**Deliverables:**
- ✅ End-to-end autonomous workflow: Issue → Clarification → Tasks → Agents → PR
- ✅ Complete documentation set
- ✅ All configuration files

### Phase 4: svg2fbf Adaptation (Week 7)

**svg2fbf-Specific Enhancements**
- [ ] Customize test-and-log.sh for session-based tests
- [ ] Configure CI guardian for svg2fbf workflows
- [ ] Setup PR enforcer with svg2fbf standards (88 chars, etc.)
- [ ] Create svg2fbf-specific agent instructions
- [ ] Test complete workflow on svg2fbf issues

**Deliverables:**
- ✅ Fully adapted CCPM for svg2fbf
- ✅ Validated on existing svg2fbf CI failures
- ✅ Documentation for svg2fbf developers

### Phase 5: Polish & Release (Week 8)

**Documentation**
- [ ] Update PLUGIN_README.md with skills documentation
- [ ] Create SKILLS.md explaining each skill
- [ ] Update PLUGIN_INSTALL.md with SERENA setup
- [ ] Create migration guide from commands to skills
- [ ] Write examples and tutorials

**Testing**
- [ ] Integration tests for each skill
- [ ] End-to-end workflow tests
- [ ] Performance benchmarks
- [ ] Security audit

**Release**
- [ ] Version 2.0.0 release
- [ ] Update CHANGELOG.md
- [ ] Create release notes
- [ ] Publish to plugin marketplace (when available)

---

## Migration Strategy

### Backward Compatibility

**Keep existing commands operational:**
- All 45 existing commands remain functional
- Commands now internally use skills when available
- Graceful degradation if skills disabled

**Example migration:**

```markdown
# Old: /pm:issue-start 1234
# Behavior: User manually starts issue

# New: Skills enabled
# Behavior:
#   1. issue-orchestrator already processed #1234
#   2. Tasks already decomposed
#   3. Agents already assigned
#   4. User just approves execution or it auto-starts

# Transition: /pm:issue-start still works
# But now it checks: "Issue already processed by orchestrator?"
# If yes: Show status and continue
# If no: Fall back to old behavior
```

### Configuration

**Enable/disable skills:**

```yaml
# .claude/skills-config.yml
skills:
  project_intelligence:
    enabled: true
    auto_run_on_init: true
    relearn_interval_days: 7

  ci_guardian:
    enabled: true
    polling_interval_minutes: 15
    auto_create_issues: true
    require_approval: false

  pr_enforcer:
    enabled: true
    auto_comment: true
    auto_fix: false
    block_merge_on_errors: true

  issue_orchestrator:
    enabled: true
    auto_validate: true
    auto_decompose: true
    auto_assign_agents: true
    auto_execute: false  # Require human approval

  deep_search:
    enabled: true
    model: claude-haiku-4-5
```

**Migration command:**

```bash
/pm:migrate-to-skills
```

This command:
1. Creates `.claude/skills-config.yml` with defaults
2. Runs initial project learning
3. Creates `.claude/learned/` directory
4. Generates project profile
5. Tests all skills
6. Provides migration report

---

## Success Metrics

### Quantitative Metrics

1. **CI Failure Response Time**
   - Current: Manual detection (hours to days)
   - Target: Auto-detection + issue creation (< 15 minutes)

2. **PR Validation Coverage**
   - Current: Manual review
   - Target: 100% automated validation

3. **Issue Processing Time**
   - Current: Manual decomposition (30-60 minutes)
   - Target: Auto-decomposition (< 5 minutes)

4. **Agent Utilization**
   - Current: Sequential execution
   - Target: 80%+ parallel execution rate

5. **Code Quality**
   - Current: Variable (depends on human review)
   - Target: 100% compliance with project standards

### Qualitative Metrics

1. **Developer Experience**
   - Reduced context switching
   - Faster issue resolution
   - Less manual project management overhead

2. **Code Consistency**
   - All PRs meet formatting standards
   - Consistent test coverage
   - Standardized documentation

3. **Team Collaboration**
   - Clear issue status visibility
   - Transparent agent progress
   - Better human-AI handoffs

---

## Risk Mitigation

### Risk 1: Skills Over-Automation

**Risk:** Skills make autonomous decisions that break things

**Mitigation:**
- All destructive actions require human approval (configurable)
- Dry-run mode for testing
- Comprehensive logging of all skill actions
- Easy rollback mechanisms
- Conservative defaults (auto_execute: false)

### Risk 2: Learning Inaccuracies

**Risk:** Skills learn incorrect project patterns

**Mitigation:**
- Confidence scoring on all learning
- Evidence-based analysis (cite sources)
- Manual validation checkpoints
- Learning history with timestamps
- Ability to manually correct learned data

### Risk 3: GitHub API Rate Limits

**Risk:** Frequent polling hits GitHub API limits

**Mitigation:**
- Configurable polling intervals
- Webhook support (when available)
- Caching of API responses
- Smart polling (only check changed resources)
- Fallback to manual triggers

### Risk 4: Complex Project Structures

**Risk:** Skills fail to understand unusual project layouts

**Mitigation:**
- Graceful degradation to command mode
- Manual override configurations
- Custom learning scripts
- Fallback to deep-search agent for analysis
- User education on edge cases

### Risk 5: SERENA MCP Dependency

**Risk:** SERENA not available or fails

**Mitigation:**
- Auto-detection of SERENA availability
- Fallback to traditional file operations
- Clear warnings when SERENA unavailable
- Documentation of SERENA benefits vs fallback
- Optional dependency (skills work without, but slower)

---

## Appendix A: Configuration File Reference

### `.claude/learned/project-profile.json`

Complete project configuration discovered by project-intelligence skill.

```json
{
  "$schema": "https://ccpm.automaze.io/schemas/project-profile.json",
  "version": "1.0",
  "created": "2025-01-13T10:00:00Z",
  "last_updated": "2025-01-13T14:30:00Z",

  "project": {
    "name": "svg2fbf",
    "type": "python-package",
    "description": "SVG to Frame-By-Frame SVG converter",
    "repository": "https://github.com/user/svg2fbf",
    "python_version": "3.12",
    "package_manager": "uv"
  },

  "test_system": {
    "framework": "pytest",
    "config_file": "pyproject.toml",
    "test_types": [
      {
        "name": "unit",
        "location": "tests/test_*.py",
        "execution": "pytest tests/",
        "output": "terminal",
        "count": 47
      },
      {
        "name": "e2e_frame_comparison",
        "location": "tests/sessions/test_session_*_*frames/",
        "execution": "pytest tests/sessions/",
        "structure": {
          "input": "input_frames/",
          "runs": "runs/YYYYMMDD_HHMMSS/",
          "output": "runs/*/output/",
          "comparison": "runs/*/comparison/",
          "report": "runs/*/report.html"
        },
        "custom_options": [
          "--html-report",
          "--image-tolerance=0.04",
          "--pixel-tolerance=0.0039",
          "--max-frames=50",
          "-v"
        ],
        "count": 14
      }
    ],
    "custom_plugins": [
      {
        "name": "pytest_frame_comparison",
        "file": "tests/conftest.py",
        "capabilities": ["image_diff", "tolerance_config", "html_reports"]
      }
    ]
  },

  "ci_pipelines": {
    "quality": {
      "file": ".github/workflows/quality.yml",
      "triggers": ["push", "pull_request"],
      "runs": ["ruff-format", "ruff-lint", "trufflehog"],
      "critical": true
    },
    "ci": {
      "file": ".github/workflows/ci.yml",
      "triggers": ["push", "pull_request"],
      "runs": ["unit-tests"],
      "critical": true
    },
    "e2e": {
      "file": ".github/workflows/e2e.yml",
      "triggers": ["push", "pull_request"],
      "runs": ["frame-comparison-tests"],
      "critical": true,
      "timeout_minutes": 30
    }
  },

  "quality_standards": {
    "formatter": "ruff",
    "formatter_config": {
      "line_length": 88,
      "quote_style": "double",
      "indent_style": "space"
    },
    "linter": "ruff",
    "linter_config": {
      "select": ["E", "F", "W", "I"],
      "ignore": []
    },
    "type_checker": "mypy",
    "type_checker_config": {
      "python_version": "3.12",
      "strict": false
    },
    "security_scanner": "trufflehog"
  },

  "pre_commit_hooks": {
    "ruff": {
      "stages": ["pre-commit"],
      "args": ["--fix"]
    },
    "ruff-format": {
      "stages": ["pre-commit"]
    },
    "trufflehog": {
      "stages": ["pre-push"]
    }
  },

  "task_runners": {
    "justfile": {
      "commands": {
        "sync": "uv sync",
        "sync-dev": "uv sync --all-extras --dev",
        "test": "pytest tests/",
        "build": "uv build",
        "reinstall": "uv pip install -e .",
        "clean": "rm -rf dist/ build/"
      }
    }
  },

  "documentation": {
    "project_docs": {
      "location": ".",
      "files": ["README.md", "CONTRIBUTING.md", "DEVELOPMENT.md", "CHANGELOG.md"]
    },
    "standard_docs": {
      "location": "FBF.SVG/docs/",
      "purpose": "FBF.SVG standard specification",
      "separate_from_project": true
    }
  },

  "learning_metadata": {
    "last_learned": "2025-01-13T14:30:00Z",
    "learning_method": "automated_discovery",
    "confidence": 0.95,
    "validation_status": "tested",
    "sources": [
      "pyproject.toml",
      "tests/conftest.py",
      ".github/workflows/*.yml",
      ".pre-commit-config.yaml",
      "justfile"
    ]
  }
}
```

### `.claude/skills-config.yml`

Master configuration for all CCPM skills.

```yaml
# CCPM Skills Configuration
# Version: 2.0.0

skills:
  # Skill #1: Project Self-Configuration
  project_intelligence:
    enabled: true
    auto_run_on_init: true
    relearn_interval_days: 7
    confidence_threshold: 0.8

    discovery:
      test_systems: true
      ci_pipelines: true
      quality_standards: true
      pre_commit_hooks: true
      task_runners: true
      documentation: true
      developer_workflow: true

    serena_integration: true
    deep_search_integration: true

  # Skill #2: CI Monitoring & Auto-Issue
  ci_guardian:
    enabled: true
    polling_interval_minutes: 15

    monitoring:
      workflows: [quality.yml, ci.yml, e2e.yml]
      auto_detect_workflows: true

    issue_creation:
      enabled: true
      deduplicate_window_hours: 24
      max_issues_per_workflow: 3
      labels: [ci-failure, auto-created]
      require_approval: false

    agent_assignment:
      enabled: true
      default_agents: [code-analyzer, test-runner]
      auto_spawn: false  # Create issue but don't auto-start agents

    learning:
      track_failure_patterns: true
      suggest_preventions: true

  # Skill #3: PR Validation & Enforcement
  pr_enforcer:
    enabled: true

    validation:
      formatting:
        enabled: true
        enforce: true
        tools: [ruff]

      linting:
        enabled: true
        enforce: true
        tools: [ruff]
        error_on_warnings: false

      type_checking:
        enabled: true
        enforce: true
        tools: [mypy]

      testing:
        enabled: true
        enforce: false
        min_coverage: 80

      documentation:
        enabled: true
        enforce: false
        require_docstrings: true

      security:
        enabled: true
        enforce: true
        tools: [trufflehog]

    auto_fix:
      enabled: true
      allowed_fixes: [formatting, import-sorting]
      require_approval: true

    github_actions:
      create_workflow: true
      workflow_file: .github/workflows/ccpm-pr-validation.yml

  # Skill #4: Autonomous Issue Management
  issue_orchestrator:
    enabled: true
    polling_interval_minutes: 30

    processing:
      auto_validate: true
      auto_clarify: true
      auto_decompose: true
      auto_assign_agents: true
      auto_execute: false  # Require human approval to start

    validation:
      require_acceptance_criteria: true
      require_technical_context: true
      require_issue_links: false

    decomposition:
      max_tasks_per_epic: 10
      min_task_hours: 1
      max_task_hours: 8
      prefer_parallelization: true

    worktrees:
      enabled: true
      location: ../worktrees
      cleanup_on_merge: true

    notifications:
      comment_on_epic: true
      comment_on_tasks: true
      update_frequency_minutes: 60

  # Agent: Deep Search (Haiku 4.5)
  deep_search:
    enabled: true
    model: claude-haiku-4-5
    context_window: 1048576  # 1MB
    temperature: 0.1
    max_tokens: 4096

    capabilities:
      codebase_analysis: true
      pattern_detection: true
      structural_analysis: true
      impact_analysis: true

# Integration Settings
integrations:
  serena_mcp:
    enabled: true
    required: false
    fallback_mode: traditional_file_ops

  github:
    require_auth: true
    api_rate_limit_buffer: 100
    prefer_webhooks: false
    fallback_to_polling: true

# Global Settings
global:
  log_level: info
  log_file: .claude/logs/skills.log
  cache_dir: .claude/cache/
  learned_dir: .claude/learned/

  dry_run: false  # Set to true for testing without actions
  require_human_approval: false  # Global override for all auto-actions
```

---

## Appendix B: Enhanced Agent Definitions

### parallel-worker Agent (Enhanced)

```markdown
# parallel-worker Agent

You are the parallel work coordinator for CCPM.

## NEW CAPABILITIES (v2.0 Skills-Based)

### Integration with Skills

You now receive rich context from skills:

1. **Project Profile** from project-intelligence skill
   - Test system structure
   - CI pipeline configuration
   - Quality standards to enforce
   - Task runner commands

2. **Issue Decomposition** from issue-orchestrator skill
   - Pre-analyzed task breakdown
   - Agent assignments per task
   - Parallelization flags
   - Dependency graph

### Enhanced Workflow

**Before (v1.0):**
- Receive epic description
- Manually analyze for parallelization
- Spawn generic sub-agents
- Hope they understand project structure

**After (v2.0):**
- Receive epic with learned project context
- Pre-decomposed tasks with agent assignments
- Spawn specialized agents with project-specific instructions
- Monitor using CI guardian skill for real-time feedback

### Example Invocation

**OLD:**
```
Task: Implement gradient support
[You figure out everything from scratch]
```

**NEW:**
```
Task: Implement gradient support (#456)

Project Context:
- Test system: Unit tests + E2E frame comparison
- Test command: pytest tests/ with custom options
- Quality: ruff (88 chars), mypy strict
- CI: quality.yml, ci.yml, e2e.yml

Task Breakdown (from issue-orchestrator):
1. Core parsing (#457) - @code-analyzer - 4h - Can parallelize
2. Interpolation (#458) - @code-analyzer - 6h - Can parallelize
3. E2E tests (#459) - @test-runner - 3h - Depends on #457, #458
4. Documentation (#460) - @file-analyzer - 2h - Depends on #459

Worktree: epic/456-gradient-support
Quality Enforcement: PR will be validated by pr-enforcer skill

Your job:
- Spawn code-analyzer for tasks #457 and #458 in parallel
- Wait for completion
- Spawn test-runner for task #459
- Wait for validation
- Spawn file-analyzer for task #460
- Monitor CI guardian for any failures
- Consolidate results for PR
```

### Instructions to Sub-Agents

When spawning sub-agents, include:

```
Project: svg2fbf (Python 3.12, uv package manager)

Test Execution:
- Unit tests: pytest tests/ -v
- E2E tests: pytest tests/sessions/ with custom options
- Output: tests/sessions/*/runs/YYYYMMDD_HHMMSS/

Quality Standards:
- Format: ruff format --line-length 88
- Lint: ruff check
- Types: mypy --strict

After completing code:
1. Run ruff format and ruff check
2. Run mypy
3. Run pytest tests/ (unit tests)
4. Create E2E test session if applicable
5. Run pytest tests/sessions/ (E2E tests)
6. Report results

CI will auto-validate via ci-guardian skill.
```

### Monitoring Integration

Monitor CI guardian for failures:

```python
# Check for new CI failures on your branch
ci_failures = await ci_guardian.check_branch("epic/456-gradient-support")

if ci_failures:
    # Failures detected, re-assign to appropriate agent
    for failure in ci_failures:
        if failure.type == "test":
            await spawn(test-runner, task=f"Fix {failure.test_name}")
        elif failure.type == "lint":
            await spawn(code-analyzer, task=f"Fix linting in {failure.file}")
```

## Output Format

Return structured summary:

```json
{
  "epic": "#456",
  "status": "completed",
  "tasks_completed": 4,
  "tasks_failed": 0,
  "total_time_hours": 12,
  "estimated_time_hours": 15,
  "parallel_efficiency": 0.83,
  "ci_status": "passing",
  "pr_validation": "passed",
  "ready_for_merge": true,
  "summary": "All 4 tasks completed. CI passing. PR validation passed.",
  "files_modified": [
    "src/svg_parser.py",
    "src/gradient_utils.py",
    "tests/test_gradient.py",
    "tests/sessions/test_session_015_gradients/",
    "FBF.SVG/docs/spec.md"
  ]
}
```
```

---

## Conclusion

This transformation plan converts CCPM from a manual command-based system into an intelligent, autonomous, skills-based workflow system that:

✅ **Learns** project structure automatically (test systems, CI, quality standards)
✅ **Adapts** to project-specific toolchains (svg2fbf's complex test structure)
✅ **Monitors** CI/CD pipelines and creates issues automatically
✅ **Validates** PRs against project standards (88 char line length, etc.)
✅ **Orchestrates** autonomous agent teams for issue resolution
✅ **Integrates** with SERENA MCP for intelligent navigation
✅ **Preserves** backward compatibility with existing commands

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 implementation (Weeks 1-2)
3. Test on svg2fbf project throughout development
4. Iterate based on real-world usage

**Questions for User:**
1. Is the 8-week timeline acceptable?
2. Should any skills be prioritized differently?
3. Are the auto-execution defaults (require_approval: false/true) appropriate?
4. Any additional svg2fbf-specific requirements?
