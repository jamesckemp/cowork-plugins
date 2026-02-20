# Linear Issue Importer

Extract issues from documents and import them into Linear — directly from Claude Code.

## What it does

Point this plugin at any document — meeting transcript, bug list, Granola note, or raw notes — and it will:

1. **Extract** actionable issues (bugs, tasks, feature requests) from the content
2. **Let you configure** the Linear team, labels, assignee, project, and parent issue
3. **Check for duplicates** before creating anything
4. **Create issues** in Linear with properly formatted descriptions
5. **Generate a summary** of everything that was created, skipped, or removed

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- Linear MCP server connected (`mcp__claude_ai_Linear__*` tools available)

## Installation

Add this plugin to Claude Code:

```bash
claude plugin add /path/to/linear-issue-importer
```

## Usage

```
/import-issues path/to/document.md    # Full import — creates issues in Linear
/preview-issues path/to/document.md   # Dry run — extract and configure only, nothing created
```

Use `/preview-issues` first to verify extraction quality before committing to a real import.

### Supported document types

| Type | Example |
|------|---------|
| Granola JSON export | Meeting recording with transcript |
| Granola Obsidian note | Meeting notes synced to Obsidian vault |
| Markdown bug list | Categorized bug reports with "Bug:", "UX:" prefixes |
| Raw transcript | Speaker-labeled meeting transcript |
| General document | Any structured document with actionable items |

### Examples

```bash
# Import bugs from a walkthrough document
/import-issues /path/to/walkthrough-bugs.md

# Import action items from a Granola meeting note
/import-issues /path/to/Obsidian/Granola/2026-02-20_Team_Sync.md

# Import from a Granola JSON export
/import-issues /path/to/meeting-export.json
```

## Workflow

1. **Extract** — the plugin reads your file and identifies issues
2. **Review** — you see a numbered list of extracted issues with suggested types and priorities
3. **Configure** — pick your Linear team, labels, and other settings
4. **Confirm** — approve, remove, or edit issues before creation
5. **Import** — duplicate check runs, then issues are created in Linear
6. **Summary** — get a markdown summary with links to all created issues

For 10+ issues, the plugin can use parallel agents grouped by category to speed up creation.

## Issue types

The plugin detects three types of issues and uses the appropriate description template:

- **Bug report** — Describe the bug / Steps to reproduce / Expected / Actual behavior
- **Action item** — Task / Context / Acceptance criteria
- **Feature request** — Description / Problem it solves / Suggested approach

Every issue includes a source attribution linking back to the original document.

## Author

James Kemp
