# Installing CCPM as a Claude Code Plugin

This guide explains how to install CCPM (Claude Code PM) as a proper Claude Code plugin.

## What is CCPM?

CCPM (Claude Code PM) is a comprehensive project management plugin for Claude Code that enables:

- **Spec-driven development** - Transform PRDs into epics, epics into tasks, tasks into code
- **GitHub Issues integration** - Use GitHub as your project database
- **Parallel agent execution** - Multiple AI agents working simultaneously
- **Git worktree isolation** - Clean separation for parallel work
- **Full traceability** - Complete audit trail from idea to production

## Installation Methods

### Method 1: Direct Installation (Recommended)

```bash
# Navigate to your project
cd /path/to/your/project

# Install CCPM
curl -sSL https://automaze.io/ccpm/install | bash
```

### Method 2: Manual Installation from Local Copy

If you have a local copy of CCPM (like in this repository):

```bash
# From your project root
cd /path/to/your/project

# Create .claude directory if it doesn't exist
mkdir -p .claude

# Copy CCPM plugin to your project
cp -r /path/to/svg2fbf/ccpm/ccpm/* .claude/

# Copy plugin manifest (optional, for plugin managers)
cp /path/to/svg2fbf/ccpm/plugin.json .claude/ccpm-plugin.json
```

### Method 3: Clone from GitHub

```bash
# From your project root
cd /path/to/your/project

# Clone CCPM into temporary directory
git clone https://github.com/automazeio/ccpm /tmp/ccpm-install

# Create .claude directory if it doesn't exist
mkdir -p .claude

# Copy plugin files
cp -r /tmp/ccpm-install/ccpm/* .claude/

# Copy plugin manifest
cp /tmp/ccpm-install/plugin.json .claude/ccpm-plugin.json

# Clean up
rm -rf /tmp/ccpm-install
```

## Post-Installation Setup

After installing CCPM, you need to initialize it:

### 1. Initialize the PM System

```bash
/pm:init
```

This command will:
- Install GitHub CLI (if needed)
- Authenticate with GitHub
- Install gh-sub-issue extension for parent-child relationships
- Create required directories
- Update .gitignore

### 2. Create or Update CLAUDE.md

If you don't have a CLAUDE.md file yet:

```bash
/init include rules from .claude/CLAUDE.md
```

If you already have a CLAUDE.md file:

```bash
/re-init
```

This will add CCPM-specific rules to your existing CLAUDE.md.

### 3. Prime the Context System

```bash
/context:create
```

This creates project-wide context files that persist across sessions.

## Verifying Installation

To verify CCPM is installed correctly:

```bash
# Check available commands
/pm:help

# Validate system integrity
/pm:validate

# Check system status
/pm:status
```

## Plugin Structure

After installation, your `.claude` directory should look like this:

```
.claude/
├── agents/            # Task-oriented agents
├── commands/          # Command definitions
│   ├── context/       # Context management
│   ├── pm/            # Project management commands
│   └── testing/       # Test execution
├── context/           # Project-wide context files
├── epics/             # PM workspace (add to .gitignore)
├── prds/              # Product requirement documents
├── rules/             # Operation guidelines
├── scripts/           # Utility scripts
└── hooks/             # Git hooks
```

## Configuration

### GitHub Repository

CCPM automatically detects your GitHub repository from `git remote`. To override:

```bash
export CCPM_GITHUB_REPO="owner/repo-name"
```

### Settings

Copy the example settings file:

```bash
cp .claude/settings.json.example .claude/settings.local.json
```

Edit `.claude/settings.local.json` to customize:
- Agent behavior
- GitHub integration
- Worktree locations
- Path preferences

## Quick Start

Once installed and initialized:

```bash
# 1. Create a PRD (Product Requirements Document)
/pm:prd-new my-feature

# 2. Transform PRD into technical epic
/pm:prd-parse my-feature

# 3. Break into tasks and push to GitHub
/pm:epic-oneshot my-feature

# 4. Start working on a task
/pm:issue-start 1234

# 5. Sync progress to GitHub
/pm:issue-sync 1234
```

## Updating CCPM

To update to the latest version:

```bash
# Pull latest changes
cd /path/to/ccpm
git pull origin main

# Re-copy files to your project
cp -r ccpm/* /path/to/your/project/.claude/
```

Or use the installation script again (it will overwrite existing files).

## Troubleshooting

### Commands Not Found

If `/pm:*` commands are not recognized:

1. Verify files are in `.claude/commands/pm/`
2. Restart Claude Code
3. Check CLAUDE.md includes CCPM rules

### GitHub Authentication Issues

```bash
# Re-authenticate with GitHub CLI
gh auth login

# Verify authentication
gh auth status

# Test repository access
gh repo view owner/repo-name
```

### Worktree Issues

If worktrees fail to create:

1. Ensure git version >= 2.0
2. Check available disk space
3. Verify parent directory exists

### Permission Issues

If scripts fail to execute:

```bash
# Make scripts executable
chmod +x .claude/scripts/**/*.sh
chmod +x .claude/hooks/*.sh
```

## Uninstalling

To remove CCPM from your project:

```bash
# Remove CCPM directories
rm -rf .claude/agents
rm -rf .claude/commands/pm
rm -rf .claude/commands/context
rm -rf .claude/commands/testing
rm -rf .claude/epics
rm -rf .claude/prds
rm -rf .claude/rules
rm -rf .claude/scripts
rm -rf .claude/hooks

# Remove remaining CCPM files
rm .claude/ccpm-plugin.json
```

Note: This preserves your `.claude/context/` directory in case you want to keep context files.

## Support

For help and support:

- **Documentation**: [CCPM README](https://github.com/automazeio/ccpm)
- **Issues**: [GitHub Issues](https://github.com/automazeio/ccpm/issues)
- **Author**: [@aroussi](https://x.com/aroussi)
- **Company**: [Automaze](https://automaze.io)

## License

MIT License - see [LICENSE](LICENSE) file for details.
