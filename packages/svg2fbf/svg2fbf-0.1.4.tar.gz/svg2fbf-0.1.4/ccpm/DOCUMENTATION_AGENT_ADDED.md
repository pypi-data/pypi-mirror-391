# Documentation Search Agent & Skill Added to CCPM

## Summary

Added the `ask-the-docs-agent` and `doc-search` skill to CCPM plugin to enable deep documentation searches across specification files, API references, and technical documentation.

**Date:** 2025-11-13
**Package Updated:** `ccpm-v2.0.0.zip` (now 414KB, was 406KB)

---

## What Was Added

### 1. ask-the-docs-agent ✅

**Location:** `ccpm/ccpm/agents/ask-the-docs-agent.md`

**Purpose:** Specialized agent for deep documentation searches

**Based on:** Claude Code's built-in `hound-agent` (read-only search specialist)

**Customizations for documentation:**
- Focused on specification documents, API references, configs
- Categorizes findings as: DOCUMENTED / PARTIALLY DOCUMENTED / NOT DOCUMENTED
- Provides exact quotes with source attribution
- Identifies gaps and ambiguities in documentation
- Creates structured result files for multi-question searches

**Key Features:**
- Read-only operation (never modifies files)
- Cross-document search capability
- Synonym expansion (e.g., "directory" → "dir", "folder", "path")
- Quote validation and source attribution
- Gap analysis for undocumented features

**When to use:**
- Verify if something is in specifications
- Find configuration options across docs
- Understand documented vs undocumented behavior
- Locate examples in documentation
- Cross-reference information across multiple files

### 2. doc-search Skill ✅

**Location:** `ccpm/ccpm/skills/doc-search/skill.md`

**Purpose:** Teaches how to effectively use ask-the-docs-agent

**What it provides:**
- Clear guidelines on when to use the agent
- Usage patterns and examples
- Expected output formats
- Integration with CCPM workflow
- Best practices for documentation searches
- Troubleshooting common issues

**Example usage scenarios:**
- Plugin structure questions
- Environment variable discovery
- Gap analysis for undocumented features
- CCPM-specific documentation verification

---

## How to Use

### Basic Usage

1. **Invoke the skill:**
   ```
   /skill doc-search
   ```

2. **Launch the agent with your question:**
   ```
   Launch ask-the-docs-agent to search plugin specifications for:

   Question: Can plugins have custom directories at root level?

   Files to search:
   - docs_dev/plugins-reference.md
   - docs_dev/plugins.md
   ```

3. **Review results:**
   - Agent provides categorized answer (DOCUMENTED/PARTIALLY DOCUMENTED/NOT DOCUMENTED)
   - Includes exact quotes from documentation
   - Notes gaps and ambiguities
   - Creates result file if multiple questions

### Advanced Usage - Multiple Questions

```
Launch ask-the-docs-agent for multi-question search:

Questions about CCPM plugin structure:
1. Are commands allowed in subdirectories (commands/pm/*.md)?
2. Can plugins have custom directories (rules/, scripts/)?
3. Where should user data (prds/, epics/) be stored?
4. What environment variables are available?
5. Is .zip packaging format documented?

Search all plugin specification files:
- docs_dev/plugins-reference.md
- docs_dev/plugins.md
- docs_dev/plugin-marketplaces.md
- docs_dev/settings.md

Categorize each as DOCUMENTED/PARTIALLY DOCUMENTED/NOT DOCUMENTED.
Include exact quotes and identify critical gaps.
```

---

## Integration with CCPM Workflow

### Phase 1: Before Implementation
1. Use ask-the-docs-agent to verify specifications
2. Identify what's documented vs assumed
3. Document gaps that require testing

### Phase 2: During Development
1. Query docs when uncertain
2. Keep list of undocumented behaviors
3. Test assumptions about undocumented features

### Phase 3: After Testing
1. Update docs with actual behavior
2. Note differences between docs and reality
3. Create issues for documentation gaps

---

## Example: CCPM Plugin Structure Verification

We used this agent to analyze Anthropic's plugin specifications and found:

### ✅ DOCUMENTED
- `.claude-plugin/` must be at plugin root
- Component dirs (commands/, agents/, skills/, hooks/) at root
- `${CLAUDE_PLUGIN_ROOT}` environment variable
- Installation location: `.claude/plugins/plugin-name/`

### ⚠️ PARTIALLY DOCUMENTED
- Commands in subdirectories (mentions commands/ but not nested structure)
- Agents in subdirectories (mentions agents/ but not organization)
- Skills structure (says "in subdirectories" but no examples)

### ❌ NOT DOCUMENTED
- Custom directories (rules/, scripts/, learned/)
- User data vs plugin file separation
- Packaging .zip format requirements
- File size or count limits
- Versioning strategy

**Result:** Created `docs_dev/PLUGIN_SPEC_ANALYSIS.md` documenting all findings.

---

## Agent Capabilities

### Search Tools
The agent has access to:
- **ripgrep (rg)** - Fast text search
- **grep** - Standard search
- **ag** - Code-aware search
- All standard text processing tools

### Documentation Analysis
The agent can:
1. Extract exact quotes with line numbers
2. Cross-reference across multiple files
3. Identify synonym variations
4. Find examples and code blocks
5. Detect ambiguities and contradictions
6. Categorize documentation quality

### Output Formats

**Single Question:**
```markdown
## Question: [Question]
**Answer:** [Direct answer]
**Documentation Status:** ✅/⚠️/❌
**Quote from docs:** > [Exact quote]
**Source:** filename.md, Section: "Name"
**Interpretation:** [Practical meaning]
**Gaps/Ambiguities:** [Unclear points]
```

**Multiple Questions:**
Creates file: `docs_search_results_<timestamp>_<topic>.md`
- Organized by question
- Summary of documented vs not documented
- List of critical gaps

---

## File Structure

```
ccpm/ccpm/
├── agents/
│   ├── ask-the-docs-agent.md          # NEW - Documentation search agent
│   ├── parallel-worker.md
│   ├── test-runner.md
│   ├── file-analyzer.md
│   └── code-analyzer.md
└── skills/
    └── doc-search/                     # NEW - Documentation search skill
        └── skill.md
```

---

## Updated Package

**Package:** `ccpm/ccpm-v2.0.0.zip`
**Size:** 414KB (was 406KB)
**New files included:**
- agents/ask-the-docs-agent.md
- skills/doc-search/skill.md

**To regenerate:**
```bash
cd ccpm
bash create-plugin-zip.sh
```

---

## Testing Recommendations

### Test 1: Agent Recognition
After plugin installation:
```
/agent list
```
Should show: `ask-the-docs-agent`

### Test 2: Skill Availability
```
/skill list
```
Should show: `doc-search`

### Test 3: Basic Search
```
/skill doc-search

Launch ask-the-docs-agent to search docs_dev/plugins-reference.md for:
Question: Where must plugin.json be located?
```

Expected: Returns exact quote from documentation with source.

### Test 4: Multi-Question Search
```
Launch ask-the-docs-agent to answer these questions about plugin structure:
1. Are nested commands allowed?
2. Can plugins have custom directories?
3. What environment variables are available?

Search all plugin specification files in docs_dev/
```

Expected: Creates result file with categorized answers.

---

## Benefits

### For CCPM Development
1. **Verification:** Quickly verify specifications before implementing
2. **Gap Identification:** Know what's undocumented and needs testing
3. **Decision Making:** Make informed choices based on documented behavior

### For Users
1. **Self-Service:** Find answers in documentation without asking
2. **Comprehensive:** Search across multiple files simultaneously
3. **Precise:** Get exact quotes and sources, not paraphrases

### For Documentation
1. **Quality Check:** Identify ambiguities and gaps
2. **Consistency:** Find contradictions across files
3. **Improvement:** Guide documentation updates

---

## Comparison with Other Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **ask-the-docs-agent** | Search documentation files | Questions about specs, APIs, configs |
| **hound-agent** | Search code files | Find patterns, broken refs, security issues |
| **SERENA MCP** | Search by symbol name | Known function/class names in code |
| **WebSearch** | Search online | When docs not available locally |
| **WebFetch** | Fetch web pages | Get online documentation |

---

## Next Steps

1. ✅ Agent and skill added to plugin
2. ✅ Plugin package regenerated (414KB)
3. ⏳ Install plugin in test environment
4. ⏳ Test agent with actual documentation searches
5. ⏳ Verify skill provides correct guidance
6. ⏳ Document any issues or improvements needed

---

## Quick Reference

**Invoke skill:**
```
/skill doc-search
```

**Simple search:**
```
Launch ask-the-docs-agent to find [information] in [file/directory]
```

**Multi-question:**
```
Launch ask-the-docs-agent to answer:
1. [Question 1]
2. [Question 2]
Search files: [list]
```

**Verify feature:**
```
Launch ask-the-docs-agent to verify if [feature] is documented in [specs]
```

**Gap analysis:**
```
Launch ask-the-docs-agent to identify what's NOT documented about [topic]
```

---

**Document Version:** 1.0
**Date:** 2025-11-13
**Status:** Added to Plugin ✅
**Package:** ccpm-v2.0.0.zip (414KB)
**Ready for:** Testing
