#!/usr/bin/env python3
"""
CCPM Rules Catalog Generator

Scans CCPM rules and project-specific rules to create a lightweight catalog
for progressive loading and discoverability.

Usage:
    python catalog-rules.py [--output FILE] [--claude-dir DIR]

Output:
    Creates rules-catalog.json in .claude/learned/ directory
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import argparse


def extract_title(content: str) -> str:
    """Extract the first H1 heading from markdown content."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def extract_purpose(content: str) -> str:
    """Extract the first paragraph after the title."""
    # Remove the title line
    lines = content.split("\n")
    found_title = False
    purpose_lines = []

    for line in lines:
        if line.startswith("# ") and not found_title:
            found_title = True
            continue

        if found_title:
            line = line.strip()
            # Skip empty lines
            if not line:
                if purpose_lines:  # Stop at first empty after text
                    break
                continue
            # Stop at next heading
            if line.startswith("#"):
                break
            purpose_lines.append(line)
            # Get first 2 sentences
            if len(" ".join(purpose_lines).split(".")) >= 2:
                break

    purpose = " ".join(purpose_lines)
    # Limit to ~200 chars
    if len(purpose) > 200:
        purpose = purpose[:197] + "..."
    return purpose


def extract_keywords(content: str, title: str) -> List[str]:
    """Extract relevant keywords from content."""
    # Common words to ignore
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "you",
        "your",
        "we",
        "our",
    }

    # Extract words (lowercase, alphanumeric)
    words = re.findall(r"\b[a-z]+\b", content.lower())

    # Count frequency
    word_freq = {}
    for word in words:
        if len(word) > 3 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Get top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [k for k, _ in keywords[:10]]  # Top 10

    # Add words from title (always relevant)
    title_words = [w.lower() for w in re.findall(r"\b[a-z]+\b", title.lower()) if len(w) > 3]
    for word in title_words:
        if word not in keywords:
            keywords.insert(0, word)

    return keywords[:15]  # Max 15 keywords


def categorize_rule(name: str, content: str) -> str:
    """Determine rule category based on name and content."""
    name_lower = name.lower()
    content_lower = content.lower()

    # Coordination patterns
    if "agent" in name_lower or "coordination" in name_lower:
        return "coordination"

    # Operational patterns
    operational_terms = ["operation", "worktree", "branch", "github", "datetime", "frontmatter"]
    if any(term in name_lower for term in operational_terms):
        return "operational"

    # Quality/standards patterns
    quality_terms = ["standard", "pattern", "test", "path", "ast-grep"]
    if any(term in name_lower for term in quality_terms):
        return "quality"

    # Default
    return "operational"


def determine_applies_to(name: str, keywords: List[str]) -> List[str]:
    """Determine what this rule applies to."""
    applies = []

    # From name
    if "test" in name.lower():
        applies.extend(["testing", "pytest", "validation"])
    if "worktree" in name.lower():
        applies.extend(["worktree", "parallel", "epic", "git"])
    if "github" in name.lower():
        applies.extend(["github", "issue", "pr", "cli"])
    if "agent" in name.lower():
        applies.extend(["parallel", "agents", "coordination"])
    if "branch" in name.lower():
        applies.extend(["git", "branch", "pr"])
    if "datetime" in name.lower() or "frontmatter" in name.lower():
        applies.extend(["timestamp", "frontmatter", "file-creation"])

    # From keywords
    if "test" in keywords:
        applies.extend(["testing"])
    if "worktree" in keywords:
        applies.extend(["worktree"])
    if "github" in keywords or "issue" in keywords:
        applies.extend(["github"])

    # Deduplicate
    return list(set(applies))


def determine_priority(name: str, category: str) -> str:
    """Determine rule priority."""
    critical_rules = ["github-operations", "datetime", "test-execution"]
    high_priority_rules = ["worktree-operations", "agent-coordination"]

    if name in critical_rules:
        return "critical"
    if name in high_priority_rules:
        return "high"
    if category == "operational":
        return "medium"
    return "low"


def create_load_trigger(keywords: List[str]) -> str:
    """Create a load trigger expression."""
    # Use top 3-5 keywords
    trigger_keywords = keywords[:5]
    if not trigger_keywords:
        return "false"

    keywords_list = ", ".join(f"'{k}'" for k in trigger_keywords)
    return f"task_contains([{keywords_list}])"


def analyze_rule(file_path: Path, plugin_root: Path, is_project_rule: bool = False) -> Dict:
    """Analyze a single rule file and extract metadata."""
    content = file_path.read_text()
    name = file_path.stem

    title = extract_title(content)
    purpose = extract_purpose(content)
    keywords = extract_keywords(content, title)
    category = categorize_rule(name, content)
    applies_to = determine_applies_to(name, keywords)
    priority = determine_priority(name, category)
    load_trigger = create_load_trigger(keywords)

    rule_data = {
        "name": name,
        "file": f"./{file_path.relative_to(plugin_root)}",
        "category": category,
        "purpose": purpose,
        "size_bytes": file_path.stat().st_size,
        "summary": purpose,  # For now, same as purpose
        "applies_to": applies_to,
        "keywords": keywords,
        "required_by_skills": [],  # To be filled manually or by skills
        "required_by_agents": [],  # To be filled manually or by skills
        "priority": priority,
        "load_trigger": load_trigger,
    }

    # Project rule specific fields
    if is_project_rule:
        rule_data["overrides"] = None  # To be determined by comparing names
        rule_data["extends"] = None

    return rule_data


def scan_rules(plugin_root: Path) -> tuple[List[Dict], List[Dict]]:
    """Scan CCPM rules directories.

    Note: Only scans CCPM's internal rules. Project-specific rules are NOT supported
    as they would violate Anthropic's plugin specification. Users should create SKILLS
    for project-specific behavior, not rules.
    """
    ccpm_rules = []

    # Scan CCPM rules (internal implementation only)
    ccpm_rules_dir = plugin_root / "rules"
    if ccpm_rules_dir.exists():
        for rule_file in sorted(ccpm_rules_dir.glob("*.md")):
            if rule_file.is_file():
                rule_data = analyze_rule(rule_file, plugin_root, is_project_rule=False)
                ccpm_rules.append(rule_data)

    return ccpm_rules, []  # No project rules - use skills instead


def create_catalog(ccpm_rules: List[Dict], project_rules: List[Dict]) -> Dict:
    """Create the complete rules catalog.

    Note: Rules are CCPM's internal implementation (exception to Anthropic spec).
    For project-specific behavior, users should create SKILLS, not rules.
    """
    total_size = sum(r["size_bytes"] for r in ccpm_rules)

    catalog = {
        "catalog_version": "1.0",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ccpm_rules": ccpm_rules,
        "note": "Rules are CCPM internal implementation. Users: create SKILLS for project-specific behavior.",
        "metadata": {
            "total_ccpm_rules": len(ccpm_rules),
            "total_size_bytes": total_size,
            "catalog_size_bytes": 0,  # Will be calculated after serialization
            "average_rule_size": total_size // len(ccpm_rules) if ccpm_rules else 0,
        },
    }

    return catalog


def main():
    parser = argparse.ArgumentParser(description="Generate CCPM rules catalog")
    parser.add_argument("--output", "-o", type=str, help="Output file path (default: .claude/learned/rules-catalog.json)")
    parser.add_argument("--claude-dir", "-d", type=str, help="Claude directory path (default: .claude or ccpm)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    # Determine plugin root directory
    if args.claude_dir:
        plugin_root = Path(args.claude_dir)
    else:
        # Use CLAUDE_PLUGIN_ROOT environment variable (set by Claude Code)
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if plugin_root_env:
            plugin_root = Path(plugin_root_env)
        else:
            # Fallback for local development: assume we're in plugin root or scripts subdir
            script_path = Path(__file__).resolve()
            if script_path.parent.name == "scripts":
                plugin_root = script_path.parent.parent  # Up from scripts/
            else:
                plugin_root = Path.cwd()

    if not plugin_root.exists():
        print(f"❌ Plugin root not found: {plugin_root}")
        return 1

    print(f"📁 Scanning rules in: {plugin_root}")

    # Scan rules
    ccpm_rules, project_rules = scan_rules(plugin_root)

    print(f"✅ Found {len(ccpm_rules)} CCPM rules")
    print(f"✅ Found {len(project_rules)} project rules")

    # Create catalog
    catalog = create_catalog(ccpm_rules, project_rules)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        learned_dir = plugin_root / "learned"
        learned_dir.mkdir(exist_ok=True)
        output_path = learned_dir / "rules-catalog.json"

    # Calculate catalog size
    catalog_json = json.dumps(catalog, indent=2 if args.pretty else None)
    catalog["metadata"]["catalog_size_bytes"] = len(catalog_json.encode("utf-8"))

    # Write catalog
    catalog_json = json.dumps(catalog, indent=2 if args.pretty else None)
    output_path.write_text(catalog_json)

    print(f"📝 Catalog written to: {output_path}")
    print(f"📊 Catalog size: {len(catalog_json)} bytes")
    print(f"📊 Total rules size: {catalog['metadata']['total_size_bytes']} bytes")
    print(f"📊 Savings: {catalog['metadata']['total_size_bytes'] - len(catalog_json)} bytes ({100 * (1 - len(catalog_json) / catalog['metadata']['total_size_bytes']):.1f}%)")

    return 0


if __name__ == "__main__":
    exit(main())
