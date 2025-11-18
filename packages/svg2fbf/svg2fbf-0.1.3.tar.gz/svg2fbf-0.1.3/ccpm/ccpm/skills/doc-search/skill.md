# Documentation Search Skill

## Purpose

This skill teaches you how to effectively search through technical documentation, specifications, and reference materials using the `ask-the-docs-agent`. Use this skill when you need to verify specifications, find configuration options, or understand documented vs undocumented behavior.

## When to Use This Skill

### ✅ Use ask-the-docs-agent when:

1. **Verifying Specifications**
   - "Does the plugin spec allow custom directories?"
   - "What's the required structure for skills?"
   - "Are there size limits for plugins?"

2. **Finding Configuration Options**
   - "What environment variables are available?"
   - "How do I configure marketplace sources?"
   - "What fields are required in plugin.json?"

3. **Cross-Document Searches**
   - "Search all API docs for authentication methods"
   - "Find all mentions of versioning across spec files"
   - "Locate examples of hook configurations"

4. **Gap Analysis**
   - "Is packaging format documented?"
   - "What's unclear about agent subdirectories?"
   - "List all documented vs undocumented features"

### ❌ Do NOT use ask-the-docs-agent for:

- Searching your project code (use SERENA MCP or grep)
- Web searches (use WebFetch or WebSearch)
- When you already know the exact file and location
- Editing documentation files (agent is read-only)

## How to Use

### Basic Pattern

```
/skill doc-search

[Then invoke the agent with your question]

Launch ask-the-docs-agent to search [documentation location] for [specific information].

Question: [Your specific question]

Files to search:
- docs/api-reference.md
- docs/configuration.md
- specs/plugin-spec.md
```

### Advanced Pattern - Multiple Questions

When you have several related questions:

```
Launch ask-the-docs-agent to search Anthropic plugin specifications for answers to these questions:

1. Where must skills be located in a plugin?
2. Can commands be in subdirectories?
3. What environment variables are provided?
4. Is packaging format specified?
5. Where should user data be stored?

Files to search:
- docs_dev/plugins-reference.md
- docs_dev/plugins.md
- docs_dev/plugin-marketplaces.md
- docs_dev/settings.md

For each question, categorize as: DOCUMENTED, PARTIALLY DOCUMENTED, or NOT DOCUMENTED.
Include exact quotes and sources.
```

## Understanding the Results

The agent will categorize findings as:

- **✅ DOCUMENTED & CLEAR**: Explicit information found with examples
- **⚠️ PARTIALLY DOCUMENTED**: Mentioned but lacking details
- **❌ NOT DOCUMENTED**: No mention in the documentation

### Result Format

```markdown
## Question: [Your question]

**Answer:** [Direct answer]
**Documentation Status:** [Status emoji]

**Quote from docs:**
> [Exact quote from documentation]

**Source:** filename.md, Section: "Section Name"

**Interpretation:** [What this means practically]
**Gaps/Ambiguities:** [What's still unclear]
```

## Example Usage Scenarios

### Scenario 1: Plugin Structure Question

**Context:** You're building a plugin and unsure about directory structure.

```markdown
Launch ask-the-docs-agent to answer:

Question: Can CCPM plugin have these directories at root level?
- rules/ (custom directory for markdown rules)
- scripts/ (Python and shell scripts)
- learned/ (generated JSON catalogs)
- prds/ (user-created PRD files)
- epics/ (user-created epic files)

Search docs_dev/plugins-reference.md and docs_dev/plugins.md for:
1. Explicit mentions of "custom directories"
2. Requirements for plugin root structure
3. Difference between plugin files vs user data
4. Any restrictions on directory names

Report what's documented, what's ambiguous, and what's not addressed.
```

**Expected outcome:** Clear categorization of what's allowed, unclear, or forbidden.

### Scenario 2: Environment Variable Discovery

**Context:** Scripts need to find plugin files, want to know available variables.

```markdown
Launch ask-the-docs-agent to search for environment variables:

Question: What environment variables does Claude Code provide to plugins?

Search all plugin spec files for:
- CLAUDE_PLUGIN_ROOT
- Any path-related variables
- Project directory variables
- User home directory variables
- Any documented variables for scripts

Include usage examples if found in docs.
```

**Expected outcome:** Complete list of available environment variables with usage.

### Scenario 3: Gap Analysis

**Context:** Packaging a plugin, need to know what's undocumented.

```markdown
Launch ask-the-docs-agent for gap analysis:

Questions about plugin packaging:
1. What should be at the root of the .zip file?
2. Should .claude-plugin/ be at zip root?
3. Are there size limits for plugins?
4. Are there file count limits?
5. What file types are forbidden?
6. How should versioning be handled?

Mark each as DOCUMENTED / PARTIALLY DOCUMENTED / NOT DOCUMENTED.
Identify critical gaps that affect distribution.
```

**Expected outcome:** List of documented vs undocumented packaging requirements.

## Integration with CCPM

### CCPM-Specific Documentation Searches

When working with CCPM, use this skill to verify:

```markdown
Launch ask-the-docs-agent to verify CCPM structure:

Context: CCPM has these components:
- 40+ commands in commands/pm/ (nested subdirectory)
- 11 rules in rules/ (custom directory)
- Scripts in scripts/ (custom directory)
- User data dirs: prds/, epics/ (writable directories)

Questions:
1. Are nested commands (commands/pm/*.md) documented as allowed?
2. Are custom directories (rules/, scripts/) mentioned?
3. Where should user-writable data (prds/, epics/) be located?
   - In plugin directory?
   - In project's .claude/ directory?
4. Any guidance on separating plugin files from user data?

Search all plugin specs and report exact documentation status for each.
```

## Best Practices

### 1. Be Specific
❌ "How do plugins work?"
✅ "What's the required structure for the .claude-plugin/ directory?"

### 2. List Search Locations
Always specify which documentation files to search:
```
Files to search:
- docs_dev/plugins-reference.md
- docs_dev/plugins.md
```

### 3. Use Categorized Questions
Group related questions:
```
Questions about directory structure:
1. [Question 1]
2. [Question 2]

Questions about configuration:
3. [Question 3]
4. [Question 4]
```

### 4. Request Exact Quotes
Always ask for:
- Exact quotes from docs
- Source file and section names
- Interpretation of what it means

### 5. Identify Gaps
Ask the agent to note what's NOT documented:
```
Also report:
- What was searched for but not found
- Ambiguities that need clarification
- Contradictions between different docs
```

## Troubleshooting

### Problem: Too many results

**Solution:** Narrow your search
```
Search only the "Directory Structure" section of plugins-reference.md
Focus specifically on [exact topic]
```

### Problem: No results found

**Solution:** Try synonyms
```
Search for:
- "custom directories" OR "additional directories" OR "non-standard directories"
- "user data" OR "project data" OR "writable files"
```

### Problem: Ambiguous answers

**Solution:** Ask for gap analysis
```
If documentation is ambiguous, list:
1. What it explicitly says
2. What's open to interpretation
3. What needs testing to verify
```

## Output Expectations

The agent will create:
- **Short answers**: Direct response for single clear questions
- **Result files**: `docs_search_results_<timestamp>_<topic>.md` for multi-question searches

Result files include:
- Exact quotes with attribution
- Clear documentation status for each question
- Summary of gaps and ambiguities
- Suggestions for what to test

## Integration with Development Workflow

### Step 1: Before Implementing
```
1. Use ask-the-docs-agent to verify specifications
2. Identify what's documented vs assumed
3. Document gaps that require testing
```

### Step 2: During Development
```
1. When unsure, query docs again
2. Keep a running list of undocumented behaviors
3. Test assumptions about undocumented features
```

### Step 3: After Testing
```
1. Update your documentation with actual behavior
2. Note differences between docs and reality
3. Create issue/PR for documentation gaps
```

## Related Skills

- **hound-agent**: For searching code files (not documentation)
- **SERENA MCP**: For searching project code by symbol names
- **WebSearch**: For searching online documentation or forums

## Success Criteria

You're using this skill effectively when:
- ✅ You can quickly verify if something is documented
- ✅ You get exact quotes with sources
- ✅ You know what's unclear and needs testing
- ✅ You avoid making assumptions about undocumented behavior
- ✅ You document gaps you discover

---

**Skill Version:** 1.0
**Last Updated:** 2025-11-13
**Related Agent:** ask-the-docs-agent
**Status:** Ready for use
