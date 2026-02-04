# Pings Triage Plugin

An intelligent notification triage system that helps you manage mentions and notifications across Slack, P2, and Figma.

## What it does

This plugin solves the common problem of scattered notifications across multiple platforms by:

- **Collecting all your pings** from Slack, P2, and Figma in one place
- **Deduplicating threaded conversations** - no more duplicate Linear issues when someone replies to a thread
- **Auto-detecting responses** - automatically closes Linear issues when you've already replied
- **Intelligent analysis** - categorizes each ping by action needed (Reply, Review, Acknowledge, Decide, Delegate) and priority (0-4)
- **Organized Linear issues** - creates clean, well-formatted issues in your private team with links back to source

## Key improvements over manual triage

- **Thread awareness**: Related pings are grouped together, avoiding duplicate issues
- **Response detection**: Checks if you've already responded and auto-closes the corresponding Linear issue
- **Smart prioritization**: Analyzes urgency signals to set appropriate priority
- **Configurable**: Set your Linear team ID, platform preferences, and analysis rules

## Requirements

This plugin requires:
- **context-a8c MCP** - For accessing Slack, P2, and Linear at Automattic
  - Providers used: `slack`, `wpcom`, `linear`
- **Gmail MCP** (optional) - For accessing Figma notifications via email

## Configuration

After installation, edit `config/user-config.json` to customize:

```json
{
  "linear": {
    "team_id": "YOUR_TEAM_ID",  // IMPORTANT: Use your private team
    "status_new": "Triage",
    "status_done": "Done"
  },
  "platforms": {
    "slack": {"enabled": true},
    "p2": {"enabled": true},
    "figma": {"enabled": true, "method": "gmail"}
  },
  "user": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "role": "Your role description"
  }
}
```

**Note:** Time range is automatic - the plugin uses the last fetch time from state, or looks back 30 days maximum on first run.

**CRITICAL**: Make sure `linear.team_id` points to your **private team** to avoid exposing private information to the rest of your organization.

## How to use

### First Time Setup

Run the setup command to configure the plugin:
```
"setup triage"
```

This will guide you through:
- Finding your Linear team ID
- Setting your name, email, and role
- Configuring which platforms to enable
- Setting your user context for personalized analysis

### Running Triage

**Complete triage (recommended):**
```
"triage my pings"
```

This runs the full workflow: fetch → dedupe → analyze → sync

**Individual commands:**
- `"fetch my pings"` - Only collect from platforms
- `"analyze my pings"` - Only analyze unprocessed pings
- `"sync to linear"` - Only sync analyzed pings to Linear

The plugin will:
1. Collect mentions from all enabled platforms
2. Deduplicate threaded conversations
3. Analyze each ping with personalized context
4. Create/update Linear issues in your triage inbox
5. Auto-close issues for pings you've already responded to
6. Show you a summary of what was processed

## State management

The plugin maintains state in `~/.pings-triage/state.json` to:
- Track which pings have been processed
- Remember thread relationships
- Store Linear issue mappings
- Record last sync timestamps

This prevents re-processing the same pings and enables smart deduplication.

## Created by

James Kemp (Core Product Manager for WooCommerce at Automattic)

Based on a Zapier workflow, reimagined as a Cowork plugin with improved threading and response detection.
