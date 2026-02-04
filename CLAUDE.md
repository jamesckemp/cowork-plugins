# Cowork Plugins Repository

Custom plugins for Claude Cowork - Anthropic's desktop application for agentic coding with Claude.

## About Claude Cowork

Cowork is Anthropic's desktop app that provides a persistent workspace for Claude to help with coding tasks. Plugins extend Cowork's capabilities with custom skills, commands, and workflows.

**Documentation:**
- [Claude Code Plugins Guide](https://docs.anthropic.com/en/docs/claude-code/plugins)
- [Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)

## This Repository

This repo contains personal/custom plugins that aren't published to the official plugin registry. Plugins here are installed locally or shared directly.

### Current Plugins

| Plugin | Description |
|--------|-------------|
| `pings-triage` | Smart notification triage - collects mentions from Slack, P2, Figma, analyzes what's needed, and syncs to Linear |

## Plugin Structure

Each plugin follows this structure:

```
{plugin-name}/
├── plugin.json              # Plugin manifest (name, version, description)
├── .claude-plugin/
│   └── plugin.json          # Cowork plugin metadata (must match version)
├── commands/                # Slash commands (/command-name)
│   └── {command}.md
├── skills/                  # Skills that commands invoke
│   └── {skill-name}/
│       ├── SKILL.md         # Executable skill instructions
│       ├── scripts/         # Python helpers (optional)
│       └── references/      # Reference docs for the skill
└── README.md                # User-facing documentation
```

### Commands vs Skills

- **Commands** (`/setup`, `/pings`) - User-facing entry points, defined in `commands/*.md`
- **Skills** - The actual logic that commands invoke, defined in `skills/*/SKILL.md`

A command file just points to a skill:
```yaml
---
name: pings
description: Smart triage - collects, analyzes, and syncs your pings
skill: pings-triage
---
```

---

## Versioning Requirements

**Every plugin update must include a version bump.** Claude Cowork uses the version number in `plugin.json` to detect updates. If you don't increment the version, users won't see the update.

### Semantic Versioning (SemVer)

Use `MAJOR.MINOR.PATCH` format:

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| **PATCH** - Bug fixes, small tweaks, copy changes | `2.0.0` → `2.0.1` | Fixed typo in analysis prompt |
| **MINOR** - New features, new commands, enhancements | `2.0.1` → `2.1.0` | Added Figma support |
| **MAJOR** - Breaking changes, complete rewrites | `2.1.0` → `3.0.0` | Changed config location, removed commands |

### Where to Update

Each plugin has two version locations that **must stay in sync**:

1. `{plugin}/plugin.json` - Main plugin manifest
2. `{plugin}/.claude-plugin/plugin.json` - Cowork plugin metadata

### Commit Checklist

Before committing plugin changes:

- [ ] Updated version in `plugin.json`
- [ ] Updated version in `.claude-plugin/plugin.json`
- [ ] Both versions match
- [ ] Version follows semver based on change type

---

## Plugin Development Guidelines

### Config Storage

Plugins should store user configuration in the **working folder**, not the plugin folder:
- Plugin folder is read-only when installed
- Use `.{plugin-name}/config.json` in the working directory
- Example: `.pings-triage/config.json`

### Writing Skills

Write executable skills with:
- Clear phases with specific steps
- Concrete MCP tool calls (not abstract descriptions)
- User-friendly error messages (never expose technical details like stack traces)
- Graceful degradation when things fail
- Use `AskUserQuestion` for gathering user input with skip options

### Commands

Keep commands minimal. Prefer one smart command that detects what's needed over multiple granular commands.

### MCP Dependencies

Declare MCP dependencies in `plugin.json`:
```json
{
  "compatibility": {
    "mcps": ["context-a8c"],
    "optional_mcps": ["gmail"]
  }
}
```
