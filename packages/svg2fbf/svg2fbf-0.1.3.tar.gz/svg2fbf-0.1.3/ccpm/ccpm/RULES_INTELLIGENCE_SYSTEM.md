# CCPM Rules Intelligence System

## IMPORTANT: Rules Are CCPM Internal Implementation

**CRITICAL:** Rules are CCPM's internal implementation detail and an **exception to Anthropic's plugin specification**. The Anthropic spec defines **SKILLS** as the proper extension mechanism, not rules.

**For Users:**
- ❌ DO NOT create custom rules
- ❌ DO NOT extend CCPM rules
- ✅ DO create SKILLS for project-specific behavior
- ✅ Rules are for CCPM's internal use by commands and agents

**This Document:** Explains how CCPM's internal rules are cataloged and used efficiently by skills. This is documentation of CCPM's non-orthodox implementation, not a user-extensible feature.

---

## Executive Summary

Transforms CCPM's 11 internal rules (36KB) into a discoverable, progressively-loaded knowledge system for efficient use by skills and agents.

**Problem:**
- 11 rules (36KB total) buried in `.claude/rules/`
- Only loaded when commands explicitly reference them
- Not discoverable by main Claude or skills
- No progressive loading - all-or-nothing wastes context

**Solution:**
- Rules cataloged as lightweight metadata (~7KB vs 36KB)
- Progressive loading: Load catalog always, specific rules on demand
- Skills declare required_rules for automatic loading
- Main Claude can query catalog without loading full content
- **80.5% context savings**

---

## Rules Inventory (CCPM Internal)

### 11 CCPM Rules (36KB total)

**Operational Rules (16.5KB):**
1. worktree-operations.md (2,775 bytes)
2. branch-operations.md (2,961 bytes)
3. github-operations.md (2,743 bytes)
4. datetime.md (3,684 bytes)
5. frontmatter-operations.md (1,423 bytes)
6. strip-frontmatter.md (2,114 bytes)

**Coordination Rules (4.9KB):**
7. agent-coordination.md (4,986 bytes)

**Quality Rules (10.6KB):**
8. standard-patterns.md (3,935 bytes)
9. path-standards.md (4,720 bytes)
10. test-execution.md (1,455 bytes)
11. use-ast-grep.md (5,288 bytes)

---

## Rules Catalog System

### Component 1: Lightweight Catalog

**Created by:** `catalog-rules.py` script  
**Location:** `.claude/learned/rules-catalog.json`  
**Size:** ~7KB (vs 36KB full rules)  
**Savings:** 80.5% context reduction

**Catalog Structure:**
```json
{
  "catalog_version": "1.0",
  "created": "2025-01-13T14:00:00Z",
  "note": "Rules are CCPM internal implementation. Users: create SKILLS for project-specific behavior.",
  
  "ccpm_rules": [
    {
      "name": "test-execution",
      "file": "ccpm/rules/test-execution.md",
      "category": "quality",
      "purpose": "Test execution patterns (no mocking, verbose output)",
      "size_bytes": 1455,
      "keywords": ["test", "pytest", "mock", "verbose"],
      "required_by_skills": ["ci-guardian", "pr-enforcer"],
      "priority": "critical",
      "load_trigger": "task_contains(['test', 'pytest'])"
    }
    // ... 10 more rules
  ],
  
  "metadata": {
    "total_ccpm_rules": 11,
    "total_size_bytes": 36084,
    "catalog_size_bytes": 7026
  }
}
```

### Component 2: Progressive Loading

**Level 1: Catalog Always Loaded (7KB)**
- Main Claude has catalog in memory
- Can query "what rules exist?" without loading full rules
- Enables discovery without context overhead

**Level 2: Skill-Determined Loading**
- Skills declare required_rules in config
- Rules loaded automatically when skill activates
- Example: ci-guardian requires github-operations, test-execution

**Level 3: Context-Triggered Loading**
- Task keywords match rule triggers
- Relevant rules loaded automatically
- Example: Task contains "test" → load test-execution.md

**Level 4: Explicit Loading**
- User or command requests specific rule
- Manual control when needed

**Level 5: Agent Inheritance**
- Subagents inherit loaded rules from parent
- Avoid re-loading same content

### Component 3: Skills Integration

**Each skill declares rule requirements:**

```yaml
# In skills-config.yml
skills:
  ci_guardian:
    required_rules:
      - github-operations  # CRITICAL
      - test-execution     # CRITICAL
      - datetime           # CRITICAL
      
  pr_enforcer:
    required_rules:
      - github-operations  # CRITICAL
      - test-execution     # CRITICAL
      - standard-patterns  # LOW
      - path-standards     # LOW
      
  issue_orchestrator:
    required_rules:
      - github-operations  # CRITICAL
      - agent-coordination # HIGH
      - worktree-operations # HIGH
      - datetime           # CRITICAL
```

**On skill activation:**
1. Check catalog for required_rules
2. Load each required rule (only if not already cached)
3. Cache for session duration
4. Apply rule patterns

**Example:**
```
ci-guardian activates →
  Load github-operations.md (2,743 bytes)
  Load test-execution.md (1,455 bytes)
  Load datetime.md (3,684 bytes)
  Total: 7,882 bytes (vs 36KB if all loaded)
```

---

## Benefits

**Context Efficiency:**
- Before: Load all 36KB or none
- After: Load ~7KB catalog + only needed rules
- Savings: 80.5% reduction

**Discoverability:**
- Main Claude can query available rules
- Skills know which rules they need
- No manual reference required

**Skills Integration:**
- Declarative requirements (required_rules)
- Automatic loading on activation
- Pattern application from rules

**Maintained Orthodoxy:**
- Rules remain CCPM internal (exception to spec)
- Users extend via SKILLS (proper Anthropic spec)
- No user-extensible rule system

---

## For svg2fbf: Use Skills, Not Rules

**WRONG Approach (Violates Spec):**
```
❌ Create .claude/rules/project/svg2fbf-test-structure.md
❌ Override CCPM rules with project rules
❌ Encourage users to create custom rules
```

**CORRECT Approach (Follows Spec):**
```
✅ Create svg2fbf-test-intelligence SKILL
✅ Skill learns svg2fbf test structure
✅ Skill stores learned config in .claude/learned/
✅ Skill uses CCPM's test-execution rule internally
✅ Extends behavior via skill logic, not rule overrides
```

**Example svg2fbf-test-intelligence Skill:**
```markdown
# svg2fbf-test-intelligence Skill

## Purpose
Learn and adapt to svg2fbf's dual test system (unit + session-based E2E)

## Learning Targets
1. Detect session-based test structure: tests/sessions/test_session_*/
2. Parse pyproject.toml for pytest custom options
3. Identify HTML report generation locations
4. Map test types (unit vs E2E)

## Uses CCPM Rules Internally
- test-execution.md (how to run tests)
- github-operations.md (for CI monitoring)

## Output
Stores learned configuration in:
.claude/learned/svg2fbf-test-config.json

## Integration
- ci-guardian skill uses learned config
- pr-enforcer skill uses learned config
- test-runner agent uses learned config
```

This is the **orthodox, spec-compliant approach**: Extend via SKILLS, not rules.

---

## Implementation

### catalog-rules.py Script

**Purpose:** Scan CCPM's internal rules, generate lightweight catalog

**Key Functions:**
```python
def scan_rules(claude_dir: Path):
    """Scan CCPM rules only (no project rules)."""
    ccpm_rules = []
    
    # Scan CCPM internal rules
    for rule_file in (claude_dir / 'rules').glob('*.md'):
        rule_data = analyze_rule(rule_file)
        ccpm_rules.append(rule_data)
    
    return ccpm_rules, []  # No project rules

def create_catalog(ccpm_rules, _):
    """Create catalog with note about proper extension."""
    return {
        'ccpm_rules': ccpm_rules,
        'note': 'Rules are CCPM internal. Users: create SKILLS for project-specific behavior.',
        'metadata': {...}
    }
```

**Usage:**
```bash
python ccpm/scripts/catalog-rules.py --claude-dir ccpm
```

**Output:** `ccpm/learned/rules-catalog.json` (7KB)

---

## Configuration

```yaml
# .claude/skills-config.yml
rules:
  enabled: true
  catalog_on_init: true
  progressive_loading: true
  
  # DO NOT enable project rules (violates spec)
  project_overrides: false  # Always false
```

---

## Conclusion

**What Rules Are:**
- CCPM's internal implementation detail
- Exception to Anthropic's plugin specification
- Used by CCPM commands and agents
- Cataloged for efficient progressive loading

**What Rules Are NOT:**
- User-extensible system
- Project customization mechanism
- Overridable by projects

**Proper Extension Mechanism:**
- Create SKILLS (Anthropic-specified)
- Skills can use rules internally
- Skills store learned project patterns

**Result:** CCPM maintains efficient internal rules system while remaining orthodox in user-facing extension mechanisms.

---

**Document Version:** 2.0 (Corrected)
**Date:** 2025-01-13
**Integration:** Part of CCPM 2.0 Skills Transformation
