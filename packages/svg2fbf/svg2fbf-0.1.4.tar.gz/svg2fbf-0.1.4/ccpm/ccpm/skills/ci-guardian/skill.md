# CI Guardian Skill

## Purpose

Automatically monitor CI/CD pipelines and create GitHub issues for failures with detailed error analysis and @claude mentions for AI-assisted debugging.

## What This Skill Does

When invoked, CI Guardian will:

1. **Check recent CI runs** for failures
2. **Analyze failure logs** to determine error type
3. **Create GitHub issues** automatically with detailed context
4. **Assign appropriate labels** based on failure type
5. **Track failure patterns** to identify recurring issues
6. **Mention @claude** in issues for AI-assisted analysis

## When to Use This Skill

**Manual Invocation:**
```
/skill ci-guardian
```

**Automated Monitoring (Recommended - Event-Driven):**
- Triggered by GitHub workflow events (NOT cron jobs!)
- Events: `workflow_run`, `push`, `pull_request`, `issues`
- Runs when CI completes (success or failure)
- Instant detection, no polling needed

**After PR Merge:**
- Automatically check if merge caused CI failures
- Create issues for regressions introduced

## How It Works

### Automated CI Monitoring Workflow

**Event-Driven Trigger:** Runs automatically when CI completes (via GitHub Actions `workflow_run` event)

When triggered by workflow completion or manually invoked:

1. **Get workflow run details from event:**
   ```bash
   # Triggered automatically by GitHub Actions
   RUN_ID="${{ github.event.workflow_run.id }}"
   WORKFLOW_NAME="${{ github.event.workflow_run.name }}"
   CONCLUSION="${{ github.event.workflow_run.conclusion }}"  # "failure" or "success"
   ```

   OR manually check recent runs:
   ```bash
   gh run list --limit 10 --json conclusion,headBranch,createdAt,id,name,workflowName
   ```

2. **For each failed run:**

   **Step 2a: Fetch failure logs**
   ```bash
   gh run view {run_id} --log-failed
   ```

   **Step 2b: Analyze failure type by scanning logs**

   Use pattern matching to categorize:

   - **Test failures:**
     - Grep for: `"FAILED"`, `"AssertionError"`, `"Error:"`, `"✗"`, `"tests failed"`
     - Extract: Test name, assertion message, file:line
     - Type: `test-failure`

   - **Build failures:**
     - Grep for: `"error:"`, `"failed to compile"`, `"build failed"`, `"ERROR in"`
     - Extract: Error message, file causing error
     - Type: `build-failure`

   - **Lint failures:**
     - Grep for: `"ruff"`, `"eslint"`, `"mypy"`, `"prettier"`, linter names
     - Extract: Rule violations, file:line
     - Type: `lint-failure`

   - **Dependency failures:**
     - Grep for: `"pip install"`, `"yarn install"`, `"npm ERR!"`, `"resolution failed"`
     - Extract: Package name, version conflict
     - Type: `dependency-failure`

   - **Timeout failures:**
     - Check: `conclusion: "timed_out"` or grep for `"timeout"`, `"exceeded"`
     - Type: `ci-timeout`

   - **Infrastructure failures:**
     - Grep for: `"runner"`, `"connection"`, `"network"`, `"502"`, `"503"`
     - Type: `ci-infrastructure`

   **Step 2c: Extract relevant log excerpt**
   - Get 10 lines before and 10 lines after error
   - Redact secrets/tokens if present
   - Format for GitHub issue

3. **Create GitHub issue:**

   ```bash
   gh issue create \
     --title "CI Failure: {failure_type} in {workflow_name}" \
     --label "{failure_type}" \
     --label "ci-failure" \
     --label "automated" \
     --body "$(cat <<'EOF'
   ## CI Run Failed

   **Workflow:** {workflow_name}
   **Run ID:** {run_id}
   **Branch:** {branch}
   **Commit:** {commit_sha}
   **Time:** {timestamp}
   **Run URL:** {run_url}

   ---

   ## Failure Type: {failure_type}

   **Analysis:**
   {failure_analysis}

   ---

   ## Error Summary

   ```
   {extracted_error_message}
   ```

   ---

   ## Relevant Logs

   <details>
   <summary>Click to expand full log excerpt</summary>

   ```
   {log_excerpt_with_context}
   ```

   </details>

   ---

   ## Debugging Steps

   {suggested_debugging_steps}

   ---

   @claude please analyze this CI failure and suggest fixes. Focus on:
   1. Root cause of the failure
   2. Which files/code likely caused this
   3. Suggested fix with code examples
   4. How to prevent this in the future

   EOF
   )"
   ```

4. **Assign labels based on failure type:**
   - `test-failure` - Unit/integration test failed
   - `build-failure` - Compilation/bundling failed
   - `lint-failure` - Code quality check failed
   - `dependency-failure` - Package installation failed
   - `ci-timeout` - Job exceeded time limit
   - `ci-infrastructure` - CI system issue (not code issue)
   - `regression` - Failure on previously passing branch
   - `needs-investigation` - Unclear failure type

5. **Track patterns in `.claude/learned/ci-failure-patterns.json`:**

   ```json
   {
     "tracked_since": "2025-11-13T12:00:00Z",
     "total_failures": 45,
     "failures_by_type": {
       "test-failure": 20,
       "lint-failure": 15,
       "dependency-failure": 5,
       "ci-timeout": 3,
       "build-failure": 2
     },
     "recurring_issues": [
       {
         "pattern": "Module 'foo' has no attribute 'bar'",
         "occurrences": 5,
         "first_seen": "2025-11-10",
         "last_seen": "2025-11-13",
         "related_issues": ["#123", "#145", "#156"],
         "suggested_fix": "Add type hints to foo module"
       }
     ],
     "most_failing_workflow": "test.yml",
     "most_failing_branch": "feature/experimental",
     "avg_failure_recovery_time": "2.5 hours"
   }
   ```

6. **Check for duplicate issues:**
   - Before creating issue, search existing issues:
     ```bash
     gh issue list --label ci-failure --state open --json title,body
     ```
   - If similar failure exists, comment on existing issue instead:
     ```bash
     gh issue comment {issue_number} --body "Failure recurred: {details}"
     ```

## Success Criteria

- All CI failures automatically get issues created within 15 minutes
- Issues include @claude mentions for AI assistance
- Failure analysis accurately categorizes error types
- No duplicate issues for same failure
- Patterns tracked and reported
- Issues include actionable debugging steps

## Configuration

Create `.claude/ci-guardian-config.json` to customize:

```json
{
  "monitoring_enabled": true,
  "max_runs_to_check": 10,
  "auto_assign_issues": true,
  "assignees": ["username1", "username2"],
  "notify_on_patterns": true,
  "pattern_threshold": 3,
  "ignore_workflows": ["dependabot.yml"],
  "ignore_branches": ["experimental/*"],
  "monitored_events": ["workflow_run", "push", "pull_request"],
  "labels": {
    "test_failure": ["test-failure", "needs-fix"],
    "build_failure": ["build-failure", "high-priority"],
    "lint_failure": ["lint-failure", "code-quality"]
  }
}
```

## Example Issue Created

```markdown
## CI Run Failed

**Workflow:** Test Suite
**Run ID:** 1234567890
**Branch:** feature/new-api
**Commit:** abc123def
**Time:** 2025-11-13 14:30:00 UTC
**Run URL:** https://github.com/owner/repo/actions/runs/1234567890

---

## Failure Type: test-failure

**Analysis:**
Test `test_api_endpoint` failed with AssertionError. The test expected status code 200 but received 500. This suggests the API endpoint is returning an internal server error.

---

## Error Summary

```
tests/test_api.py::test_api_endpoint FAILED
AssertionError: assert 500 == 200
  Expected: 200 (OK)
  Actual: 500 (Internal Server Error)
```

---

## Relevant Logs

<details>
<summary>Click to expand full log excerpt</summary>

```
tests/test_api.py:45: in test_api_endpoint
    response = client.get("/api/v1/users")
    assert response.status_code == 200
E   AssertionError: assert 500 == 200
E   Response body: {"error": "Database connection failed"}
```

</details>

---

## Debugging Steps

1. Check database connection configuration
2. Verify database service is running in CI
3. Check for missing environment variables
4. Review recent changes to database connection code
5. Test API endpoint locally with same database setup

---

@claude please analyze this CI failure and suggest fixes. Focus on:
1. Root cause of the failure
2. Which files/code likely caused this
3. Suggested fix with code examples
4. How to prevent this in the future
```

## Integration with Project Intelligence

CI Guardian works best when combined with project-intelligence skill:

1. **Uses detected CI system:**
   - Reads `.claude/learned/ci-config.json`
   - Knows which workflows exist
   - Knows which commands are run

2. **Matches failure to local commands:**
   - If CI runs `yarn test`, suggests running same locally
   - Provides exact reproduction steps

3. **Understands project structure:**
   - For monorepos, identifies which subproject failed
   - Suggests running subproject-specific tests

## Automated Setup (Recommended - Event-Driven)

### GitHub Actions: Event-Driven CI Monitoring

Create `.github/workflows/ci-guardian.yml`:

```yaml
name: CI Guardian

on:
  # Trigger when any workflow completes (success or failure)
  workflow_run:
    workflows: ["*"]  # Monitor all workflows
    types: [completed]

  # Trigger on push to main/master
  push:
    branches: [main, master]

  # Trigger on pull request events
  pull_request:
    types: [opened, synchronize, reopened]

  # Trigger on issue events
  issues:
    types: [opened, closed, reopened]

  # Allow manual trigger for testing
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    # Only run if a workflow failed (not on every success)
    if: github.event.workflow_run.conclusion == 'failure' || github.event_name != 'workflow_run'

    steps:
      - uses: actions/checkout@v3

      - name: Check CI Failures
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          echo "🔍 Checking for CI failures..."

          # Get the failed workflow run details
          if [ "${{ github.event_name }}" == "workflow_run" ]; then
            RUN_ID="${{ github.event.workflow_run.id }}"
            WORKFLOW_NAME="${{ github.event.workflow_run.name }}"
            BRANCH="${{ github.event.workflow_run.head_branch }}"

            echo "Failed workflow: $WORKFLOW_NAME (Run ID: $RUN_ID)"
            echo "Branch: $BRANCH"

            # Fetch failure logs
            gh run view $RUN_ID --log-failed > /tmp/failure_logs.txt

            # Analyze and create issue
            # (This would call CI Guardian skill or inline analysis)
            echo "Analysis would happen here"
          else
            # For other events, check recent failures
            gh run list --limit 10 --json conclusion,id,name,createdAt,headBranch \
              | jq '.[] | select(.conclusion=="failure")' > /tmp/recent_failures.json
          fi

      - name: Create Issue for Failure
        if: github.event.workflow_run.conclusion == 'failure'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Create GitHub issue with failure details
          gh issue create \
            --title "CI Failure: ${{ github.event.workflow_run.name }}" \
            --label "ci-failure" \
            --label "automated" \
            --body "CI workflow failed on branch ${{ github.event.workflow_run.head_branch }}

          **Workflow:** ${{ github.event.workflow_run.name }}
          **Run ID:** ${{ github.event.workflow_run.id }}
          **Branch:** ${{ github.event.workflow_run.head_branch }}
          **Run URL:** ${{ github.event.workflow_run.html_url }}

          @claude please analyze this CI failure and suggest fixes."
```

### Benefits of Event-Driven Approach

✅ **Instant Detection:** Runs immediately when CI fails (no 15-minute delay)
✅ **No Polling:** Triggered by GitHub events, not scheduled checks
✅ **Resource Efficient:** Only runs when something happens
✅ **Comprehensive Coverage:** Catches push, PR, workflow, and issue events
✅ **Context-Aware:** Has full context of what triggered the failure

## Failure Pattern Examples

CI Guardian can detect recurring patterns like:

**Pattern 1: Flaky Test**
```
Pattern: Test "test_timeout" fails intermittently
Occurrences: 5 times in last 7 days
Branches: Various
Suggestion: Add @pytest.mark.flaky decorator or increase timeout
```

**Pattern 2: Dependency Version Conflict**
```
Pattern: "Cannot resolve package 'foo' version conflict"
Occurrences: 3 times after dependency updates
Suggestion: Pin dependency versions in package.json
```

**Pattern 3: Infrastructure Issue**
```
Pattern: "Runner out of disk space"
Occurrences: 2 times on same runner
Suggestion: Add cleanup step or request larger runner
```

## Troubleshooting

**"No CI system detected"**
- Invoke `/skill project-intelligence` first to detect CI
- Ensure `.github/workflows/` or other CI config exists

**"GitHub CLI not authenticated"**
- Run `gh auth login` to authenticate
- Ensure `gh` CLI is installed

**"Cannot create issues"**
- Check GitHub token has `repo` and `issues` permissions
- Verify you're not hitting API rate limits

**"Too many duplicate issues"**
- CI Guardian checks for duplicates before creating
- If issues persist, check `.claude/learned/ci-failure-patterns.json`
- May need to close old issues or adjust pattern matching

## Best Practices

1. **Enable automated monitoring** - Don't wait for manual invocation
2. **Review patterns weekly** - Check `.claude/learned/ci-failure-patterns.json`
3. **Close resolved issues** - Keep issue tracker clean
4. **Adjust labels** - Customize in `.claude/ci-guardian-config.json`
5. **Ignore flaky workflows** - Add to `ignore_workflows` config
6. **Let @claude help** - Review AI suggestions in created issues
7. **Track metrics** - Monitor failure frequency and recovery time

## Output Example

```
🛡️ CI Guardian - Event Triggered

Event: workflow_run (Test Suite completed with failure)
Branch: feature/new-api
Commit: abc123def

---

📊 Failure Detected:

❌ Test Suite (test.yml)
   - Workflow: Test Suite
   - Branch: feature/new-api
   - Type: test-failure
   - Run ID: 1234567890
   - Issue: #234 created

---

📝 Issue Created:

**Title:** CI Failure: Test Suite
**Labels:** ci-failure, test-failure, automated
**Body:** Contains failure analysis with @claude mention

---

🔍 Pattern Check:

✅ First occurrence of this failure type
📝 Pattern tracked in .claude/learned/ci-failure-patterns.json

---

✅ Issue created instantly (event-driven - no polling delay!)
✅ @claude mentioned for AI-assisted debugging
```

---

**Skill Version:** 1.0
**Last Updated:** 2025-11-13
**Status:** Active
**Implements:** Feature 7 from Intelligence Plan
**Requires:** GitHub CLI (`gh`), project-intelligence skill (optional but recommended)
