# Rules Intelligence System - Orthodox Implementation

## ✅ Correction Complete

This document explains the corrected, Anthropic-spec-compliant implementation of CCPM's rules intelligence system.

## Critical Correction Made

**What Was WRONG (Violated Anthropic Spec):**
- ❌ Created `ccpm/rules/project/` directory for user-extensible rules
- ❌ Created `svg2fbf-test-structure.md` as "project rule"
- ❌ Documented project rules as user-facing feature
- ❌ Encouraged users to create custom rules
- ❌ Violated Anthropic's plugin specification (Skills are proper extension)

**What Is NOW CORRECT (Follows Anthropic Spec):**
- ✅ Rules are CCPM's internal implementation ONLY
- ✅ NO user-extensible rules
- ✅ NO project rules directory
- ✅ Users extend via SKILLS (proper Anthropic mechanism)
- ✅ Rules cataloged for CCPM's internal efficient use

## Anthropic Plugin Specification

**Proper Extension Mechanism:** **SKILLS**

From Anthropic's plugin spec:
- Plugins define SKILLS for specialized capabilities
- Skills are the extension points for users
- Skills can have specialized knowledge and workflows
- Skills integrate with project-specific patterns

**NOT in Spec:** Rules, project rules, rule overrides

## CCPM's Orthodox Implementation

### Rules (Internal Implementation)

**Purpose:** CCPM's internal operational knowledge  
**Status:** Exception to Anthropic spec (CCPM keeps for internal use)  
**User-Facing:** NO - Internal to CCPM commands/agents  
**Extensible:** NO - Fixed set of 11 rules  

### Rules Catalog

**Purpose:** Make CCPM's internal rules discoverable and efficiently loadable  
**Size:** 7KB catalog vs 36KB full rules (80.4% savings)  
**Usage:** Skills query catalog, load needed rules  
**User-Facing:** NO - Internal optimization  

### Skills (Proper Extension Mechanism)

**Purpose:** User-facing specialized capabilities  
**Status:** Follows Anthropic spec  
**User-Facing:** YES - This is how users extend CCPM  
**Extensible:** YES - Users create custom skills  

## Example: svg2fbf Test Structure

### ❌ WRONG Approach (What I Initially Did)

```markdown
Create: .claude/rules/project/svg2fbf-test-structure.md

Content: svg2fbf-specific test patterns as a "project rule"

Problem: Violates Anthropic spec, encourages users to create rules
```

### ✅ CORRECT Approach (Orthodox)

```markdown
Create: svg2fbf-test-intelligence SKILL

Purpose: Learn and adapt to svg2fbf's dual test system

Learning Targets:
1. Detect session-based test structure
2. Parse pyproject.toml for pytest options
3. Identify HTML report locations
4. Map test types (unit vs E2E)

Uses CCPM Rules Internally:
- test-execution.md (how to run tests)
- github-operations.md (for CI monitoring)

Output:
Stores learned configuration in:
.claude/learned/svg2fbf-test-config.json

Integration:
- ci-guardian skill uses learned config
- pr-enforcer skill uses learned config
- test-runner agent uses learned config

This is a SKILL that LEARNS project patterns, not a rule override.
```

## Implementation Details

### Files Corrected

**Removed:**
- ❌ `ccpm/rules/project/` directory
- ❌ `svg2fbf-test-structure.md` file

**Updated:**
- ✅ `catalog-rules.py` - No project rules scanning
- ✅ `RULES_INTELLIGENCE_SYSTEM.md` - Rewritten with orthodox approach

**Current Status:**
- 11 CCPM rules (internal implementation)
- 0 project rules (removed, use skills instead)
- 7,082 bytes catalog vs 36,084 bytes full rules
- 80.4% context savings

### Catalog Structure (Corrected)

```json
{
  "catalog_version": "1.0",
  "created": "2025-01-13T11:15:34Z",
  "note": "Rules are CCPM internal implementation. Users: create SKILLS for project-specific behavior.",
  
  "ccpm_rules": [
    {
      "name": "test-execution",
      "file": "ccpm/rules/test-execution.md",
      "category": "quality",
      "purpose": "Test execution patterns...",
      "size_bytes": 1455,
      "keywords": ["test", "pytest"],
      "required_by_skills": ["ci-guardian", "pr-enforcer"],
      "priority": "critical"
    }
    // ... 10 more CCPM internal rules
  ],
  
  "metadata": {
    "total_ccpm_rules": 11,
    "total_size_bytes": 36084,
    "catalog_size_bytes": 7082
  }
}
```

Note: NO `project_rules` array - removed entirely.

## Usage

### For CCPM Developers

Rules are internal implementation:
- Commands reference rules internally
- Agents use rules for patterns
- Skills load required rules from catalog
- NOT user-facing

### For Project Users

Extend CCPM via SKILLS, not rules:
1. Create a skill (follows Anthropic spec)
2. Skill learns project patterns
3. Skill stores learned config
4. Skill uses CCPM rules internally
5. Skills integrate seamlessly

## Configuration

```yaml
# .claude/skills-config.yml (Corrected)
rules:
  enabled: true
  catalog_on_init: true
  progressive_loading: true
  
  # NO project rules support
  project_overrides: false  # Always false
  
skills:
  # Proper extension mechanism
  project_intelligence:
    enabled: true
    learn_test_structure: true
    
  # Example: svg2fbf would add custom skill here
  svg2fbf_test_intelligence:
    enabled: true
    required_rules: ["test-execution"]  # Uses CCPM rules internally
```

## Benefits of Orthodox Approach

### Technical Benefits

✅ **Context Efficiency:** 80.4% savings (7KB catalog vs 36KB rules)  
✅ **Progressive Loading:** Load only needed rules  
✅ **Skill Integration:** Skills declare required_rules  
✅ **Discoverability:** Catalog enables queries  

### Architectural Benefits

✅ **Spec Compliance:** Rules internal, Skills for extension  
✅ **Clear Separation:** Internal (rules) vs External (skills)  
✅ **Maintainability:** One rule set, not per-project chaos  
✅ **Flexibility:** Projects add skills, not rules  

### User Benefits

✅ **Clear Path:** "Create a skill" is unambiguous  
✅ **Powerful:** Skills can do much more than rules  
✅ **Integrated:** Skills work with CCPM's architecture  
✅ **Standard:** Follows Anthropic's documented patterns  

## Summary

**Rules:**
- CCPM internal implementation (exception to spec)
- 11 fixed rules, not extensible
- Cataloged for efficient loading
- Used by commands/agents/skills internally

**Skills:**
- Anthropic-specified extension mechanism
- User-facing and extensible
- Can learn project patterns
- Can use rules internally
- Proper way to customize CCPM

**Result:** Orthodox implementation that respects Anthropic's specifications while maintaining CCPM's internal efficiency.

---

**Document Version:** 1.0 (Corrected Implementation)  
**Date:** 2025-01-13  
**Status:** Orthodox and Spec-Compliant  
