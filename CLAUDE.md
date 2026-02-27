# Claude Plugins Repository

Custom plugins for Claude Code - Anthropic's agentic coding tool.

## About Claude Code

Claude Code is Anthropic's CLI tool for agentic coding with Claude. Plugins extend Claude Code's capabilities with custom skills, commands, and workflows.

**Documentation:**
- [Claude Code Plugins Guide](https://docs.anthropic.com/en/docs/claude-code/plugins)
- [Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)

## This Repository

This repo contains personal/custom plugins that aren't published to the official plugin registry. Plugins here are installed locally or shared directly.

### Current Plugins

- **linear-issue-importer** (`v1.3.2`) - Extract issues from documents and import them into Linear
- **voiceprint** (`v1.5.1`) - Extract a linguistic fingerprint and generate a personalized voice profile and writer skill

## Plugin Structure

Each plugin follows this structure:

```
{plugin-name}/
├── plugin.json              # Plugin manifest (name, version, description)
├── .claude-plugin/
│   └── plugin.json          # Claude Code plugin metadata (must match version)
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

- **Commands** - User-facing entry points, defined in `commands/*.md`
- **Skills** - The actual logic that commands invoke, defined in `skills/*/SKILL.md`

A command file just points to a skill:
```yaml
---
name: my-command
description: What the command does
skill: my-skill
---
```

---

## Versioning Requirements

**Every plugin update must include a version bump.** Claude Code uses the version number in `plugin.json` to detect updates. If you don't increment the version, users won't see the update.

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
2. `{plugin}/.claude-plugin/plugin.json` - Claude Code plugin metadata

### Commit Checklist

Before committing plugin changes:

- [ ] Updated version in `plugin.json`
- [ ] Updated version in `.claude-plugin/plugin.json`
- [ ] Both versions match
- [ ] Version follows semver based on change type

### New Plugin Checklist

When adding a new plugin:

- [ ] Created `.claude-plugin/plugin.json` with name, version, description, author
- [ ] Registered in `.claude-plugin/marketplace.json` (add to `plugins` array with `name` and `source: "./plugin-dir"`)
- [ ] Listed in CLAUDE.md under "Current Plugins" with version and description

---

## Plugin Development Guidelines

### Config Storage

Plugins should store user configuration in the **working folder**, not the plugin folder:
- Plugin folder is read-only when installed
- Use `.{plugin-name}/config.json` in the working directory
- Example: `.my-plugin/config.json`

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
