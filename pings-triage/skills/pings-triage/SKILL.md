---
name: pings-triage
description: >
  Smart triage for mentions across Slack, P2, and Figma. Collects pings, analyzes what's needed,
  and syncs to Linear in one command. Use when the user says "triage my pings", "check my mentions",
  "organize my notifications", or runs /pings.
---

# Pings Triage

A single smart command that collects, analyzes, and syncs your mentions to Linear.

> **CRITICAL: Config Location**
>
> All configuration and state MUST be stored in the **current working directory**, not the plugin directory.
> The plugin directory is read-only when installed from a marketplace.
>
> Config path: `{current_working_directory}/.pings-triage/config.json`
> State path: `{current_working_directory}/.pings-triage/state.json`
>
> Always use `os.getcwd()` as the base path. **Never** attempt to write to the plugin/skill directory.

## Before You Start

Check if configured by looking for `.pings-triage/config.json` in the current working directory. If missing or invalid, tell the user:

> I need to set up pings triage first. Run `/setup` to configure your Linear team and preferences.

Then stop execution.

---

## Phase 1: Initialize

Load the required MCP providers:

```
mcp__context-a8c__context-a8c-load-provider(provider="slack")
mcp__context-a8c__context-a8c-load-provider(provider="wpcom")
mcp__context-a8c__context-a8c-load-provider(provider="linear")
```

If any provider fails to load, tell the user which one failed and suggest they check their MCP connections.

Load the config and state using the Python helpers:

```python
from scripts.state_manager import ConfigManager, StateManager
import os

base_path = os.getcwd()
config = ConfigManager(base_path)
state = StateManager(base_path)

if not config.is_valid():
    print("Config not found or invalid. Run /setup first.")
    return

enabled_platforms = config.get_enabled_platforms()
user_name = config.get("user.name")
linear_team = config.get("linear.team_id")
```

---

## Phase 2: Collect Pings

For each enabled platform, fetch mentions since the last fetch (or last 30 days for first run).

### Slack Collection

If `slack` is enabled:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="slack",
    tool="search-messages",
    params={
        "query": f"mentions:@{user_name}",
        "after": state.get_fetch_start_date("slack")
    }
)
```

For each message found:
1. Generate thread_id: `slack-{channel_id}-{thread_ts or ts}`
2. Check if user already replied in the thread
3. Add to state:

```python
ping_id = state.add_ping(
    platform="slack",
    message_id=msg["ts"],
    timestamp=msg["timestamp"],
    author=msg["user_name"],
    content=msg["text"],
    thread_id=thread_id,
    metadata={
        "channel_id": msg["channel"],
        "channel_name": msg["channel_name"],
        "permalink": msg["permalink"]
    }
)

if user_already_replied:
    state.mark_ping_responded(ping_id)
```

Update last_fetch after successful collection:
```python
state.set_last_fetch("slack")
```

### P2 Collection

If `p2` is enabled:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="wpcom",
    tool="search-mentions",
    params={
        "user": user_name,
        "after": state.get_fetch_start_date("p2")
    }
)
```

For each mention:
1. Generate thread_id: `p2-{site_id}-{post_id}`
2. Check if user already commented/liked
3. Add to state with similar pattern as Slack

Update last_fetch after successful collection:
```python
state.set_last_fetch("p2")
```

### Figma Collection (if enabled)

Figma mentions come through email notifications. If the Gmail MCP is available, search for Figma notification emails and extract mention details.

---

## Phase 3: Analyze

Get all unanalyzed pings and process them using the analysis prompt from `references/analysis-prompt.md`.

```python
unanalyzed = state.get_unanalyzed_pings()
if not unanalyzed:
    print("No new pings to analyze.")
```

For each ping, read the analysis prompt and substitute variables:
- `{USER_NAME}` → config.get("user.name")
- `{USER_CONTEXT}` → config.get_user_context()

Then analyze the ping content to determine:

| Field | Description |
|-------|-------------|
| **title** | `{Author Name}: {Brief action description}` |
| **summary** | What they need from you in 1-2 sentences |
| **suggested_action** | One of: Acknowledge, Review, Reply, Decide, Delegate |
| **priority** | 0-4 (see analysis-prompt.md for rules) |
| **specific_guidance** | Additional context if needed |

Store the analysis:
```python
state.update_ping_analysis(ping_id, {
    "title": title,
    "summary": summary,
    "suggested_action": action,
    "priority": priority,
    "specific_guidance": guidance,
    "analyzed_at": datetime.now().isoformat()
})
```

---

## Phase 4: Sync to Linear

Sync analyzed pings to Linear using the format from `references/linear-template.md`.

### For new pings (no Linear issue yet):

Check if this ping's thread already has a Linear issue:
```python
existing_issue = state.get_thread_linear_issue(ping["thread_id"])
```

**If thread has existing issue**: Add a comment to that issue about the new message.

**If no existing issue**: Create a new one:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="create-issue",
    params={
        "teamId": config.get("linear.team_id"),
        "title": analysis["title"],
        "description": format_description(analysis, ping),
        "priority": analysis["priority"]
    }
)
```

Link the issue to the ping:
```python
state.link_linear_issue(ping_id, issue["id"])
```

### For responded pings:

If response was detected and issue exists, close it:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="update-issue",
    params={
        "id": ping["linear_issue_id"],
        "stateId": "done_state_id"  # Get from team states
    }
)
```

---

## Phase 5: Present Results

Show a user-friendly summary:

```markdown
## Pings Triage Complete

**Collected:**
- Slack: X new mentions
- P2: Y new mentions

**Analyzed:**
- Priority 1 (Urgent): N
- Priority 2 (High): N
- Priority 3 (Normal): N
- Priority 4 (Low): N

**Synced:**
- Created X new Linear issues
- Updated Y existing threads
- Auto-closed Z responded issues

**Next:** [Open your Linear triage inbox →](https://linear.app/team/{team_id}/triage)
```

If no new pings were found:

> You're all caught up! No new mentions since your last triage.

---

## Error Handling

If something fails during execution:

1. **MCP provider won't load**: Tell user which provider failed, suggest checking MCP connections
2. **No config found**: Direct to `/setup`
3. **Linear API error**: Show the error, suggest checking team ID in config
4. **Platform fetch fails**: Continue with other platforms, note which one failed

Never expose technical details like stack traces or raw API errors. Translate to user-friendly messages.

---

## References

- `references/analysis-prompt.md` - Complete analysis logic and output format
- `references/linear-template.md` - Linear issue formatting and threading strategy
- `references/platform-guide.md` - Platform-specific MCP tool details
