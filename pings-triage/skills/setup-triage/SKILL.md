---
name: setup-triage
description: >
  Configure pings triage - set up your Linear team, user context, and platform preferences.
  Use when the user says "setup triage", "configure pings", runs /setup, or when /pings
  reports missing configuration.
---

# Setup Triage

Interactive wizard to configure pings triage. Uses AskUserQuestion for all user input with Skip options.

---

> **CRITICAL: Config Location**
>
> All configuration MUST be stored in the **current working directory**, not the plugin directory.
> The plugin directory is read-only when installed from a marketplace.
>
> Config path: `{current_working_directory}/.pings-triage/config.json`
>
> Always use `os.getcwd()` as the base path. **Never** attempt to write to the plugin/skill directory.

---

## Phase 1: Detect Existing Config

Check if config already exists:

```python
from scripts.state_manager import ConfigManager
import os

config = ConfigManager(os.getcwd())
is_reconfiguring = config.exists()
```

If reconfiguring, tell the user:

> I found your existing configuration. I'll walk through the settings - skip any you want to keep unchanged.

If first time:

> Let's set up pings triage. I'll ask a few questions to configure your preferences.

---

## Phase 2: Load Linear Teams and User

Load the Linear provider and fetch available teams AND the current user:

```
mcp__context-a8c__context-a8c-load-provider(provider="linear")

mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="list-teams",
    params={}
)

mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="me",
    params={}
)
```

If Linear provider fails:

> I couldn't connect to Linear. Make sure the context-a8c MCP is configured and try again.

Stop execution.

**Store the user ID immediately:**
```python
config.set("linear.user_id", me_response["id"])
```

---

## Phase 3: Linear Team Selection

Present the teams using AskUserQuestion. Format teams as options showing name and key.

**Important**: Warn about using private teams. Add "(Personal)" or "(Recommended)" to teams that appear to be personal.

```
AskUserQuestion({
    questions: [{
        question: "Which Linear team should receive your triage issues? Choose your private/personal team to keep your pings confidential.",
        header: "Linear team",
        options: [
            { label: "JCK - James Kemp Personal (Recommended)", description: "Your private team - keeps pings confidential" },
            { label: "WOO - WooCommerce", description: "Shared team - others can see your pings" },
            // ... other teams
        ],
        multiSelect: false
    }]
})
```

Store the selected team ID:
```python
config.set("linear.team_id", selected_team_id)
```

---

## Phase 4: User Context

Gather user context for personalized analysis. Use AskUserQuestion with Skip options - user can provide custom text via the "Other" option.

### 4.1 Name and Email

If reconfiguring and values exist, show current values in the description.

```
AskUserQuestion({
    questions: [{
        question: "What's your name? This helps personalize the analysis.",
        header: "Your name",
        options: [
            { label: "James Kemp", description: "Use this name" },
            // If reconfiguring, current value as first option
        ],
        multiSelect: false
    }]
})
```

```python
config.set("user.name", user_name)
config.set("user.email", user_email)  # Can be gathered similarly or skipped
```

### 4.2 Role

```
AskUserQuestion({
    questions: [{
        question: "What's your role? This helps determine what types of pings need your attention.",
        header: "Your role",
        options: [
            { label: "Product Manager", description: "Product decisions and roadmap" },
            { label: "Engineering Lead", description: "Technical decisions and team management" },
            { label: "Designer", description: "Design decisions and reviews" },
            { label: "Engineering Manager", description: "Team management and processes" }
        ],
        multiSelect: false
    }]
})
```

```python
config.set("user.role", user_role)
```

### 4.3 Responsibilities Context

```
AskUserQuestion({
    questions: [{
        question: "What are you responsible for? This helps prioritize which pings matter most.",
        header: "Context",
        options: [
            { label: "Product decisions for a specific area", description: "You make product calls for your domain" },
            { label: "Cross-functional coordination", description: "You connect multiple teams/areas" },
            { label: "Technical architecture", description: "You guide technical direction" },
            { label: "Team delivery", description: "You ensure your team ships successfully" }
        ],
        multiSelect: true
    }]
})
```

If the user provides custom text (via "Other"), use that as-is for the context.

```python
config.set("user.context", user_context_string)
```

---

## Phase 5: Platform Configuration

Configure which platforms to monitor.

```
AskUserQuestion({
    questions: [{
        question: "Which platforms should I monitor for mentions?",
        header: "Platforms",
        options: [
            { label: "Slack (Recommended)", description: "Monitor Slack mentions and DMs" },
            { label: "P2", description: "Monitor P2 post mentions and comments" },
            { label: "Figma", description: "Monitor Figma comment notifications via email" }
        ],
        multiSelect: true
    }]
})
```

```python
for platform in ["slack", "p2", "figma"]:
    config.set(f"platforms.{platform}.enabled", platform in selected_platforms)
```

---

## Phase 6: Verify MCP Connections

Test that required MCPs are available:

```
mcp__context-a8c__context-a8c-load-provider(provider="slack")  # if Slack enabled
mcp__context-a8c__context-a8c-load-provider(provider="wpcom")  # if P2 enabled
mcp__context-a8c__context-a8c-load-provider(provider="linear") # always required
```

Report status for each:
- Slack: (connected) or (not connected - Slack pings won't work)
- P2: (connected) or (not connected - P2 pings won't work)
- Linear: (connected) or (required - setup cannot complete)

If Linear is not connected, stop and tell the user to configure the context-a8c MCP.

---

## Phase 7: Save Configuration

Save the complete config:

```python
config.save()
print(f"Configuration saved to: {config.config_file}")
```

---

## Phase 8: Confirm Setup

Show a summary of what was configured:

```markdown
## Setup Complete!

**Linear:**
- Team: {team_name} ({team_id})
- User ID: {user_id} (for issue assignment)
- New issues go to: Triage status
- Completed issues: Done status

**You:**
- Name: {name}
- Role: {role}

**Monitoring:**
- Slack: Enabled
- P2: Enabled
- Figma: Disabled

**Next steps:**
Run `/pings` to collect and triage your mentions!
```

---

## Configuration Schema

The config is saved to `.pings-triage/config.json` in the current working directory:

```json
{
  "version": "3.1.0",
  "linear": {
    "team_id": "JCK",
    "user_id": "abc123-def456",
    "status_new": "Triage",
    "status_done": "Done"
  },
  "platforms": {
    "slack": { "enabled": true },
    "p2": { "enabled": true },
    "figma": { "enabled": false }
  },
  "user": {
    "name": "James Kemp",
    "email": "jamesckemp@gmail.com",
    "role": "Core Product Manager for WooCommerce",
    "context": "Makes product decisions for WooCommerce Core. Tagged for product direction, roadmap questions, and feature prioritization."
  },
  "state": {
    "last_fetch": {},
    "pings": {},
    "threads": {},
    "synced_urls": [],
    "metadata": {
      "version": "3.1.0",
      "created_at": "2024-01-15T10:00:00Z"
    }
  }
}
```

---

## Error Handling

- **Linear MCP fails**: Cannot complete setup. Tell user to check MCP configuration.
- **User skips all questions**: Create minimal config with defaults, warn that analysis may be generic.
- **Team list empty**: User may not have Linear access. Suggest they check their Linear account.
- **Write permission error**: Warn user that config may not persist, suggest checking folder permissions.

---

## Re-running Setup

Setup is safe to run multiple times:
- Shows current values as first options
- User can skip to keep existing values
- Only updates what user explicitly changes
- Preserves existing state data (pings, threads, synced_urls)
