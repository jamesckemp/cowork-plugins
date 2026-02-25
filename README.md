# Claude Plugins

Custom plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - Anthropic's agentic coding tool.

## Plugins

- **linear-issue-importer** - Extract issues from documents and import them into Linear
- **voiceprint** - Build a voice profile from your writing and generate a personalized writer skill

## Installation

### With Claude Code CLI

```bash
claude plugin add --marketplace github:jamesckemp/claude-plugins
```

Then install individual plugins:

```bash
claude plugin install linear-issue-importer
claude plugin install voiceprint
```

### With Claude Code (Desktop App)

1. In Claude Code, click the **+** button in the Plugins panel
2. Select **Browse plugins**
3. Click the marketplace dropdown and select **Add marketplace from GitHub**
4. Enter `jamesckemp/claude-plugins`
5. Click **Sync**

The plugins will appear in your marketplace and can be installed from there.

## Documentation

- [Claude Code Plugins Guide](https://docs.anthropic.com/en/docs/claude-code/plugins)
- [Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)

## License

Personal use.
