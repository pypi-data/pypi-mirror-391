---
allowed-tools: Bash, Read, Write
---

# Epic Merge

Merge completed epic from worktree back to main branch.

## Usage
```
/pm:epic-merge <epic_name>
```

## Quick Check

1. **Verify worktree exists:**
   ```bash
   git worktree list | grep "epic-$ARGUMENTS" || echo "❌ No worktree for epic: $ARGUMENTS"
   ```

2. **Check for active agents:**
   Read `.claude/epics/$ARGUMENTS/execution-status.md`
   If active agents exist: "⚠️ Active agents detected. Stop them first with: /pm:epic-stop $ARGUMENTS"

## Instructions

### 1. Pre-Merge Validation

Navigate to worktree and check status:
```bash
cd ../epic-$ARGUMENTS

# Check for uncommitted changes
if [[ $(git status --porcelain) ]]; then
  echo "⚠️ Uncommitted changes in worktree:"
  git status --short
  echo "Commit or stash changes before merging"
  exit 1
fi

# Check branch status
git fetch origin
git status -sb
```

### 1.5. Git Safety: .gitignore Validation

**BEFORE MERGING**, verify no .gitignored files were committed:

```bash
cd ../epic-$ARGUMENTS

# Read .gitignore patterns from project root
if [ -f "../../.gitignore" ]; then
  echo "🔍 Checking for .gitignored files in branch..."

  # Get all files in the branch that differ from main
  git diff --name-only main...HEAD > /tmp/changed_files.txt

  # Check each file against .gitignore patterns
  while read -r file; do
    # Use git check-ignore to see if file matches .gitignore
    if git check-ignore -q "$file"; then
      echo "⚠️ WARNING: $file matches .gitignore pattern but is committed!"
      echo "   This file should not be in git. Remove with: git rm --cached '$file'"
      echo "   Pattern matched: $(git check-ignore -v "$file" | cut -d: -f2-)"
    fi
  done < /tmp/changed_files.txt

  # Special checks for dangerous files
  if git diff --name-only main...HEAD | grep -qE '\.(env|env\.local|env\.production|credentials|secrets|pem|key)$'; then
    echo "❌ ERROR: Detected secret/credential files in branch!"
    echo "   Files found:"
    git diff --name-only main...HEAD | grep -E '\.(env|env\.local|env\.production|credentials|secrets|pem|key)$'
    echo "   NEVER commit these files! Remove them immediately:"
    echo "   git rm --cached <file> && git commit --amend"
    exit 1
  fi

  # Check if .claude/learned/ files are being merged (usually shouldn't be)
  if git diff --name-only main...HEAD | grep -q '\.claude/learned/'; then
    echo "⚠️ Note: .claude/learned/ files detected in branch"
    echo "   These are auto-generated project configurations."
    echo "   Usually these should be in .gitignore. Continue? (yes/no)"
  fi

  echo "✅ Git safety check passed"
fi
```

**Success Criteria:** No files matching .gitignore patterns are merged to main.

### 2. Test Verification Before Merge (REQUIRED)

**Read test configuration:**
```bash
cd ../epic-$ARGUMENTS

# Check if project-intelligence config exists
if [ -f ".claude/learned/project-config.json" ]; then
  # Use learned test command from project intelligence
  TEST_CMD=$(jq -r '.test.command // empty' .claude/learned/project-config.json)
  if [ -n "$TEST_CMD" ]; then
    echo "📝 Using configured test command: $TEST_CMD"
  fi
fi

# Fallback: Detect test command from project type if not configured
if [ -z "$TEST_CMD" ]; then
  echo "⚠️ No test config found in .claude/learned/project-config.json"
  echo "Run /skill project-intelligence to configure project tests"
  echo "Falling back to auto-detection..."

  if [ -f package.json ]; then
    TEST_CMD="npm test"
  elif [ -f pom.xml ]; then
    TEST_CMD="mvn test"
  elif [ -f build.gradle ] || [ -f build.gradle.kts ]; then
    TEST_CMD="./gradlew test"
  elif [ -f pyproject.toml ] || [ -f setup.py ]; then
    TEST_CMD="pytest -v"
  elif [ -f Cargo.toml ]; then
    TEST_CMD="cargo test"
  elif [ -f go.mod ]; then
    TEST_CMD="go test ./..."
  elif [ -f Makefile ] && grep -q "^test:" Makefile; then
    TEST_CMD="make test"
  else
    echo "⚠️ No test framework detected. Skipping tests."
    TEST_CMD=""
  fi
fi
```

**Run tests with logging:**
```bash
if [ -n "$TEST_CMD" ]; then
  echo "🧪 Running test suite before merge..."

  # Create log directory
  mkdir -p .claude/test-logs

  # Run tests and log output
  TEST_LOG=".claude/test-logs/$(date +%Y%m%d_%H%M%S)_pre-merge.log"
  $TEST_CMD 2>&1 | tee "$TEST_LOG"
  TEST_EXIT_CODE=${PIPESTATUS[0]}

  if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    TEST_SUMMARY=$(tail -5 "$TEST_LOG")
    echo "Test summary: $TEST_SUMMARY"
  else
    echo "❌ Tests failed!"
    echo ""
    echo "Test log saved to: $TEST_LOG"
    echo ""
    echo "Options:"
    echo "  1. Fix tests now (RECOMMENDED)"
    echo "  2. Commit anyway (NOT RECOMMENDED - will likely break CI)"
    echo "  3. Abort merge"
    echo ""
    read -p "Your choice (1/2/3): " choice

    case $choice in
      1)
        echo "Please fix the failing tests and re-run /pm:epic-merge $ARGUMENTS"
        exit 1
        ;;
      2)
        echo "⚠️ WARNING: Proceeding with failing tests!"
        echo "Note: This merge will include note about failing tests"
        ;;
      3)
        echo "Merge aborted"
        exit 1
        ;;
      *)
        echo "Invalid choice. Aborting merge."
        exit 1
        ;;
    esac
  fi
else
  echo "ℹ️ No tests to run (test command not configured)"
fi
```

**Success Criteria:** Merge only proceeds if tests pass OR user explicitly overrides (with warning).

### 3. Update Epic Documentation

Get current datetime: `date -u +"%Y-%m-%dT%H:%M:%SZ"`

Update `.claude/epics/$ARGUMENTS/epic.md`:
- Set status to "completed"
- Update completion date
- Add final summary

### 4. Attempt Merge

```bash
# Return to main repository
cd {main-repo-path}

# Ensure main is up to date
git checkout main
git pull origin main

# Attempt merge
echo "Merging epic/$ARGUMENTS to main..."
git merge epic/$ARGUMENTS --no-ff -m "Merge epic: $ARGUMENTS

Completed features:
# Generate feature list
feature_list=""
if [ -d ".claude/epics/$ARGUMENTS" ]; then
  cd .claude/epics/$ARGUMENTS
  for task_file in [0-9]*.md; do
    [ -f "$task_file" ] || continue
    task_name=$(grep '^name:' "$task_file" | cut -d: -f2 | sed 's/^ *//')
    feature_list="$feature_list\n- $task_name"
  done
  cd - > /dev/null
fi

echo "$feature_list"

# Extract epic issue number
epic_github_line=$(grep 'github:' .claude/epics/$ARGUMENTS/epic.md 2>/dev/null || true)
if [ -n "$epic_github_line" ]; then
  epic_issue=$(echo "$epic_github_line" | grep -oE '[0-9]+' || true)
  if [ -n "$epic_issue" ]; then
    echo "\nCloses epic #$epic_issue"
  fi
fi"
```

### 5. Handle Merge Conflicts

If merge fails with conflicts:
```bash
# Check conflict status
git status

echo "
❌ Merge conflicts detected!

Conflicts in:
$(git diff --name-only --diff-filter=U)

Options:
1. Resolve manually:
   - Edit conflicted files
   - git add {files}
   - git commit
   
2. Abort merge:
   git merge --abort
   
3. Get help:
   /pm:epic-resolve $ARGUMENTS

Worktree preserved at: ../epic-$ARGUMENTS
"
exit 1
```

### 6. Post-Merge Cleanup

If merge succeeds:
```bash
# Push to remote
git push origin main

# Clean up worktree
git worktree remove ../epic-$ARGUMENTS
echo "✅ Worktree removed: ../epic-$ARGUMENTS"

# Delete branch
git branch -d epic/$ARGUMENTS
git push origin --delete epic/$ARGUMENTS 2>/dev/null || true

# Archive epic locally
mkdir -p .claude/epics/archived/
mv .claude/epics/$ARGUMENTS .claude/epics/archived/
echo "✅ Epic archived: .claude/epics/archived/$ARGUMENTS"
```

### 7. Update GitHub Issues

Close related issues:
```bash
# Get issue numbers from epic
# Extract epic issue number
epic_github_line=$(grep 'github:' .claude/epics/archived/$ARGUMENTS/epic.md 2>/dev/null || true)
if [ -n "$epic_github_line" ]; then
  epic_issue=$(echo "$epic_github_line" | grep -oE '[0-9]+$' || true)
else
  epic_issue=""
fi

# Close epic issue
gh issue close $epic_issue -c "Epic completed and merged to main"

# Close task issues
for task_file in .claude/epics/archived/$ARGUMENTS/[0-9]*.md; do
  [ -f "$task_file" ] || continue
  # Extract task issue number
  task_github_line=$(grep 'github:' "$task_file" 2>/dev/null || true)
  if [ -n "$task_github_line" ]; then
    issue_num=$(echo "$task_github_line" | grep -oE '[0-9]+$' || true)
  else
    issue_num=""
  fi
  if [ ! -z "$issue_num" ]; then
    gh issue close $issue_num -c "Completed in epic merge"
  fi
done
```

### 8. Final Output

```
✅ Epic Merged Successfully: $ARGUMENTS

Summary:
  Branch: epic/$ARGUMENTS → main
  Commits merged: {count}
  Files changed: {count}
  Issues closed: {count}
  
Cleanup completed:
  ✓ Worktree removed
  ✓ Branch deleted
  ✓ Epic archived
  ✓ GitHub issues closed
  
Next steps:
  - Deploy changes if needed
  - Start new epic: /pm:prd-new {feature}
  - View completed work: git log --oneline -20
```

## Conflict Resolution Help

If conflicts need resolution:
```
The epic branch has conflicts with main.

This typically happens when:
- Main has changed since epic started
- Multiple epics modified same files
- Dependencies were updated

To resolve:
1. Open conflicted files
2. Look for <<<<<<< markers
3. Choose correct version or combine
4. Remove conflict markers
5. git add {resolved files}
6. git commit
7. git push

Or abort and try later:
  git merge --abort
```

## Important Notes

- Always check for uncommitted changes first
- Run tests before merging when possible
- Use --no-ff to preserve epic history
- Archive epic data instead of deleting
- Close GitHub issues to maintain sync