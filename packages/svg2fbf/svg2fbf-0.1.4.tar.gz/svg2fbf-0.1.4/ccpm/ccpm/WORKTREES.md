# Git Worktrees in CCPM

## Overview

CCPM uses git worktrees to enable parallel development on multiple issues/epics simultaneously without conflicts. Each epic/issue can have its own isolated working directory while sharing the same git repository.

## Why Worktrees?

**Traditional git workflow problems:**
- Can only work on one branch at a time
- Switching branches loses uncommitted changes
- Stashing/unstashing is error-prone
- Can't run tests on one branch while coding on another

**Worktree solution:**
- Multiple working directories from single repository
- Each worktree has its own branch
- Switch between issues instantly
- Run tests in one worktree while coding in another
- Parallel AI agent execution on different issues

## Worktree Locations

### Default Location

CCPM creates worktrees in: `../worktrees/` (relative to project root)

**Example structure:**
```
/Users/you/Projects/
├── svg2fbf/                        # Main repository
│   ├── src/
│   ├── tests/
│   └── .git/
└── worktrees/                      # Worktree directory
    ├── epic-456-gradient-support/  # Epic #456 worktree
    │   ├── src/
    │   ├── tests/
    │   └── .git  (file pointing to main .git)
    └── epic-789-filter-support/    # Epic #789 worktree
        ├── src/
        ├── tests/
        └── .git  (file pointing to main .git)
```

### Why Parent Directory?

Worktrees are placed in parent directory to:
1. Keep main repository clean
2. Avoid .gitignore conflicts
3. Allow easy discovery (`ls ../worktrees/`)
4. Prevent accidental commits of worktree files

## Creating Worktrees

### Manual Creation

```bash
# Create worktree for epic/issue
git worktree add ../worktrees/epic-456-gradient-support -b epic/456-gradient-support

# Navigate to worktree
cd ../worktrees/epic-456-gradient-support

# Work normally
git status
git add .
git commit -m "Implement gradient parsing"
```

### CCPM Automatic Creation

When using `/pm:epic-start-worktree <epic-name>`, CCPM automatically:
1. Creates worktree in `../worktrees/epic-{number}-{name}/`
2. Creates branch `epic/{number}-{name}`
3. Configures agents to work in worktree
4. Tracks worktree in epic metadata

## Working with Worktrees

### List All Worktrees

```bash
# Show all worktrees
git worktree list

# Example output:
# /Users/you/Projects/svg2fbf            abc123f [main]
# /Users/you/Projects/worktrees/epic-456 def456g [epic/456-gradient-support]
# /Users/you/Projects/worktrees/epic-789 ghi789j [epic/789-filter-support]
```

### Switch Between Worktrees

Simply `cd` to different directories - no branch switching needed!

```bash
# Work on epic 456
cd ../worktrees/epic-456-gradient-support
git status

# Switch to epic 789
cd ../worktrees/epic-789-filter-support
git status

# Return to main
cd ~/Projects/svg2fbf
git status
```

### Commit Changes in Worktree

Work exactly as you would in main repository:

```bash
cd ../worktrees/epic-456-gradient-support

# Make changes
vim src/gradient_utils.py

# Commit normally
git add src/gradient_utils.py
git commit -m "Add gradient interpolation"

# Push to remote
git push -u origin epic/456-gradient-support
```

## Cleanup

### When Epic is Complete

After merging epic PR:

**Option 1: CCPM Automatic Cleanup** (Recommended)
```bash
/pm:epic-merge <epic-name>
```

This command:
- Verifies PR is merged
- Removes worktree
- Deletes local branch
- Cleans up epic metadata

**Option 2: Manual Cleanup**
```bash
# Remove worktree
git worktree remove ../worktrees/epic-456-gradient-support

# Delete local branch
git branch -d epic/456-gradient-support

# Delete remote branch (if needed)
git push origin --delete epic/456-gradient-support
```

### Cleanup All Merged Worktrees

```bash
# List all worktrees
git worktree list

# For each merged epic:
git worktree remove ../worktrees/epic-XXX-name

# Prune removed worktrees
git worktree prune
```

### Force Remove Stuck Worktree

If worktree has uncommitted changes:

```bash
# Force remove (DESTRUCTIVE - loses uncommitted work)
git worktree remove --force ../worktrees/epic-456-gradient-support
```

### Clean Entire Worktrees Directory

**WARNING: This removes ALL worktrees!**

```bash
# List what will be deleted
ls -la ../worktrees/

# Remove all worktrees (DESTRUCTIVE)
rm -rf ../worktrees/*

# Clean git worktree tracking
git worktree prune
```

## Best Practices

### 1. One Epic Per Worktree

- Create separate worktree for each epic
- Don't reuse worktrees for different epics
- Clean up after merging

### 2. Keep Worktrees Short-Lived

- Create when starting work
- Delete immediately after merging
- Don't accumulate old worktrees

### 3. Regular Cleanup

Run weekly:
```bash
# Check for merged branches
git branch --merged main

# Remove corresponding worktrees
git worktree list
git worktree remove ../worktrees/epic-XXX-name
git worktree prune
```

### 4. Disk Space Monitoring

Each worktree is a full copy of the working directory (but shares .git objects):

```bash
# Check worktree sizes
du -sh ../worktrees/*

# Example output:
# 150M  ../worktrees/epic-456-gradient-support
# 150M  ../worktrees/epic-789-filter-support
```

If disk space is limited, clean up merged worktrees promptly.

## Troubleshooting

### "Worktree already exists"

```bash
# Error: worktree '../worktrees/epic-456' already exists

# Solution: Remove old worktree first
git worktree remove ../worktrees/epic-456-gradient-support
```

### "Branch already checked out"

```bash
# Error: branch 'epic/456' is already checked out at '../worktrees/epic-456'

# Solution: Use different branch name or remove existing worktree
git worktree list  # Find where branch is checked out
git worktree remove <path-from-list>
```

### Worktree Path Doesn't Exist

```bash
# Error: worktree path doesn't exist

# Solution: Git tracking is out of sync, prune and recreate
git worktree prune
git worktree add ../worktrees/epic-456-gradient-support -b epic/456-gradient-support
```

### Uncommitted Changes Blocking Removal

```bash
# Error: worktree contains modified or untracked files

# Option 1: Commit or stash changes first
cd ../worktrees/epic-456-gradient-support
git status
git add .
git commit -m "WIP: Save progress"

# Option 2: Force remove (loses changes!)
git worktree remove --force ../worktrees/epic-456-gradient-support
```

### Parent Directory Doesn't Exist

```bash
# Error: '../worktrees' does not exist

# Solution: Create directory first
mkdir -p ../worktrees
git worktree add ../worktrees/epic-456-gradient-support -b epic/456-gradient-support
```

## Configuration

### Custom Worktree Location

To use a different worktree directory, edit `.claude/skills-config.yml`:

```yaml
skills:
  issue_orchestrator:
    worktrees:
      enabled: true
      location: /path/to/custom/worktrees  # Absolute path
      cleanup_on_merge: true
```

**Examples:**
```yaml
# Use /tmp for temporary worktrees
location: /tmp/ccpm-worktrees

# Use dedicated SSD for performance
location: /mnt/fast-ssd/worktrees

# Use home directory
location: ~/ccpm-worktrees
```

### Disable Worktrees

If you prefer traditional branch switching:

```yaml
skills:
  issue_orchestrator:
    worktrees:
      enabled: false
```

This makes CCPM work in main repository with branch switching instead of worktrees.

## Advanced Usage

### Worktree for Quick Testing

```bash
# Create temporary worktree to test changes
git worktree add ../worktrees/test-changes -b test/quick-experiment

cd ../worktrees/test-changes
# Make experimental changes
# Run tests
# If good, merge; if bad, just delete worktree

git worktree remove ../worktrees/test-changes
git branch -D test/quick-experiment
```

### Worktree for CI/CD

```bash
# Create worktree for automated testing
git worktree add ../worktrees/ci-build -b ci/automated-build

cd ../worktrees/ci-build
# Run full test suite without affecting main development
pytest tests/
npm run build

# Cleanup
git worktree remove ../worktrees/ci-build
```

### Multiple Agents in Parallel

```bash
# Agent 1 works on parsing
cd ../worktrees/epic-456-gradient-support
# Make changes to src/gradient_parser.py

# Agent 2 works on interpolation (same epic, different worktree!)
# NOTE: Usually one worktree per epic, but for true parallelism:
git worktree add ../worktrees/epic-456-task-2 -b epic/456-task-2
cd ../worktrees/epic-456-task-2
# Make changes to src/gradient_interpolation.py

# Merge both when done
```

## Security Considerations

### Secrets in Worktrees

- Each worktree is a separate directory
- `.env` files are NOT shared between worktrees
- Be careful with secrets in multiple worktrees

**Best practice:**
- Use `.env.example` in repository
- Copy to `.env` in each worktree
- Add `.env` to `.gitignore`

### File Permissions

Worktrees inherit permissions from main repository:
- Ensure `../worktrees/` directory has appropriate permissions
- Check permissions if seeing access errors

```bash
# Check permissions
ls -ld ../worktrees/

# Fix if needed
chmod 755 ../worktrees/
```

## Performance

### Disk Usage

- Worktrees share git objects (commits, blobs, trees)
- Only working directory files are duplicated
- Typical overhead: ~same size as working directory

```bash
# Check main repo size
du -sh .git/

# Check worktree size (only working files, not .git)
du -sh ../worktrees/epic-456-gradient-support/
```

### Speed

- Creating worktree: ~instant (just checks out files)
- Switching: instant (just `cd`)
- Commits: same speed as main repo
- Cleanup: instant

## Integration with svg2fbf

### svg2fbf-Specific Considerations

**Test Sessions:**
- Each worktree has its own `tests/sessions/` directory
- Session test runs are independent
- Cleanup worktree also removes all session test runs

**Example:**
```
worktrees/epic-456-gradient-support/
├── tests/
│   └── sessions/
│       └── test_session_015_gradients/
│           └── runs/
│               ├── 20250113_140000/  # From this worktree
│               └── 20250113_150000/
```

**Build Artifacts:**
- Each worktree can have its own `dist/`, `build/` directories
- `uv` virtual environments are shared (in `.venv/`)
- Clean up build artifacts before removing worktree

## FAQ

**Q: Can I have multiple worktrees from different branches?**
A: Yes! Each worktree can be on any branch. That's the whole point.

**Q: Do worktrees share uncommitted changes?**
A: No. Each worktree has completely independent working directory.

**Q: Can I commit in one worktree and see it in another?**
A: Yes. Commits are in shared repository, so `git pull` in other worktree shows them.

**Q: What happens if I delete `../worktrees/` directory manually?**
A: Git will think worktrees still exist. Run `git worktree prune` to clean up tracking.

**Q: Can I move a worktree to different directory?**
A: Yes, but you must tell git: `git worktree move <old-path> <new-path>`

**Q: Do hooks run in worktrees?**
A: Yes. Git hooks and pre-commit hooks run normally in each worktree.

**Q: Is it safe to delete main repository while worktrees exist?**
A: No! Worktrees depend on main repository's `.git/` directory. Delete worktrees first.

## References

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [CCPM Worktree Operations Rule](rules/worktree-operations.md)
- [CCPM Epic Start Worktree Command](commands/pm/epic-start-worktree.md)

---

**Last Updated:** 2025-01-13
**CCPM Version:** 2.0.0
