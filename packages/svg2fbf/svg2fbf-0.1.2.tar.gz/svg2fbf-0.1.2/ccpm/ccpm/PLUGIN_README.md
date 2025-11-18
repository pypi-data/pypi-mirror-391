# CCPM Claude Code Plugin

[![Claude Code](https://img.shields.io/badge/Plugin-Claude%20Code-d97757)](https://github.com/automazeio/ccpm)
[![MIT License](https://img.shields.io/badge/License-MIT-28a745)](LICENSE)
[![Automaze](https://img.shields.io/badge/By-automaze.io-4b3baf)](https://automaze.io)

This directory contains CCPM packaged as a proper Claude Code plugin.

## What's Different About the Plugin Version?

The plugin version includes:

### ✅ Standard Plugin Manifest (`plugin.json`)
- Proper metadata and versioning
- Command registration
- Agent definitions
- Dependency specifications
- Installation instructions

### ✅ Enhanced Discoverability
- Plugin managers can detect and install CCPM automatically
- Commands are registered with descriptions
- Agents are documented and discoverable

### ✅ Dependency Management
- Declares required dependencies (gh CLI, git)
- Specifies optional extensions (gh-sub-issue)
- Version requirements clearly stated

### ✅ Standardized Structure
- Follows Claude Code plugin conventions
- Compatible with future plugin ecosystem
- Easier to maintain and update

## Plugin Manifest Details

The `plugin.json` file defines:

**Core Information:**
- Name: `ccpm`
- Version: `1.0.0`
- Display Name: Claude Code PM
- Author: Automaze (automazeio)
- License: MIT

**Commands:** 45 slash commands including:
- PM workflow commands (`/pm:*`)
- Context management (`/context:*`)
- Testing utilities (`/testing:*`)
- Code review (`/code-rabbit`)

**Agents:** 4 specialized agents:
- parallel-worker - Execute parallel work streams
- test-runner - Run and validate tests
- file-analyzer - Analyze file changes
- code-analyzer - Analyze code quality

**Rules:** 11 operational guidelines:
- Worktree operations
- GitHub integration
- Path standards
- Agent coordination
- Test execution
- And more...

**Hooks:** Git workflow enhancements
- bash-worktree-fix - Fix bash worktree issues

**Scripts:** 17 utility scripts for PM operations

## Using the Plugin

### Installation

See [PLUGIN_INSTALL.md](PLUGIN_INSTALL.md) for detailed installation instructions.

**Quick install:**
```bash
curl -sSL https://automaze.io/ccpm/install | bash
```

### Commands

After installation, all commands are available via slash commands:

```bash
/pm:help              # Show all commands
/pm:prd-new feature   # Start new feature
/pm:epic-oneshot      # Decompose and sync
/pm:issue-start 1234  # Begin work
/pm:status            # Check progress
```

### Configuration

The plugin includes example configuration:

```bash
# Copy example settings
cp .claude/settings.json.example .claude/settings.local.json

# Edit settings
vim .claude/settings.local.json
```

## Plugin vs Traditional Installation

| Aspect | Plugin Version | Traditional Version |
|--------|---------------|---------------------|
| **Installation** | Single command | Manual copy |
| **Discovery** | Plugin managers | Manual search |
| **Updates** | Version tracking | Git pull + copy |
| **Dependencies** | Declared in manifest | Documented separately |
| **Commands** | Registered automatically | Manual integration |
| **Documentation** | Embedded in manifest | Separate files |

## Plugin Structure

```
ccpm/
├── plugin.json              # ← Plugin manifest (NEW)
├── PLUGIN_README.md         # ← Plugin documentation (NEW)
├── PLUGIN_INSTALL.md        # ← Installation guide (NEW)
├── README.md                # Original CCPM README
├── ccpm/                    # Plugin content
│   ├── agents/              # 4 specialized agents
│   ├── commands/            # 45 slash commands
│   │   ├── pm/              # Project management
│   │   ├── context/         # Context management
│   │   └── testing/         # Test execution
│   ├── rules/               # 11 operational guidelines
│   ├── scripts/             # 17 utility scripts
│   ├── hooks/               # Git workflow hooks
│   ├── context/             # Context storage
│   ├── epics/               # PM workspace
│   └── prds/                # PRD storage
├── doc/                     # Multilingual docs
└── LICENSE                  # MIT License
```

## Version History

### 1.0.0 (Current)
- Initial plugin manifest
- All 45 commands registered
- 4 agents defined
- 11 rules documented
- 17 scripts included
- Installation guide created
- Plugin README added

## Dependencies

### Required

| Dependency | Version | Purpose |
|------------|---------|---------|
| **gh** | >=2.0.0 | GitHub CLI for issue management |
| **git** | >=2.0.0 | Version control and worktrees |

### Optional

| Dependency | Purpose |
|------------|---------|
| **gh-sub-issue** | Parent-child issue relationships |

### Installation Check

```bash
# Verify dependencies
gh --version
git --version

# Check gh authentication
gh auth status

# Check for gh-sub-issue extension
gh extension list | grep sub-issue
```

## Plugin Development

### Adding Commands

1. Create command file in `ccpm/commands/`
2. Add entry to `plugin.json` commands array
3. Document in COMMANDS.md

### Adding Agents

1. Create agent file in `ccpm/agents/`
2. Add entry to `plugin.json` agents array
3. Document in AGENTS.md

### Adding Rules

1. Create rule file in `ccpm/rules/`
2. Add entry to `plugin.json` rules array
3. Reference in commands as needed

### Updating Version

1. Update version in `plugin.json`
2. Update CHANGELOG.md
3. Create git tag
4. Push to repository

## Future Enhancements

Planned features for future versions:

- [ ] Plugin marketplace integration
- [ ] Automatic updates via plugin manager
- [ ] Configuration UI
- [ ] Enhanced dependency checking
- [ ] Multi-language support in manifest
- [ ] Plugin health checks
- [ ] Performance monitoring
- [ ] Usage analytics (opt-in)

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) in the main repository.

## Support

- **Documentation**: See main [README.md](README.md)
- **Installation Help**: See [PLUGIN_INSTALL.md](PLUGIN_INSTALL.md)
- **Issues**: [GitHub Issues](https://github.com/automazeio/ccpm/issues)
- **Contact**: [@aroussi](https://x.com/aroussi)

## License

MIT License - Copyright (c) Automaze

See [LICENSE](LICENSE) file for full text.

---

**Ship faster with Automaze.** Visit [automaze.io](https://automaze.io) to learn more.
