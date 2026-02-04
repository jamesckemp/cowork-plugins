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

Load the config using the Python helper (ConfigManager now handles both config and state):

```python
from scripts.state_manager import ConfigManager
import os

base_path = os.getcwd()
config = ConfigManager(base_path)

if not config.is_valid():
    print("Config not found or invalid. Run /setup first.")
    return

enabled_platforms = config.get_enabled_platforms()
user_name = config.get("user.name")
linear_team = config.get("linear.team_id")
```

### Ensure Linear User ID

If `linear.user_id` is not set, fetch it from Linear's `me` API and store it:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="me",
    params={}
)
```

```python
if not config.get("linear.user_id"):
    # After calling Linear me API
    config.set("linear.user_id", me_response["id"])
    config.save()
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
        "after": config.get_fetch_start_date("slack")
    }
)
```

For each message found:
1. Generate thread_id: `slack-{channel_id}-{thread_ts or ts}`
2. Check if user already replied in the thread
3. Add to state:

```python
ping_id = config.add_ping(
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
    config.mark_ping_responded(ping_id)
```

Update last_fetch after successful collection:
```python
config.set_last_fetch("slack")
```

### P2 Collection

If `p2` is enabled:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="wpcom",
    tool="search-mentions",
    params={
        "user": user_name,
        "after": config.get_fetch_start_date("p2")
    }
)
```

For each mention:
1. Generate thread_id: `p2-{site_id}-{post_id}`
2. Check if user already commented/liked
3. Add to state with similar pattern as Slack

Update last_fetch after successful collection:
```python
config.set_last_fetch("p2")
```

### Figma Collection (if enabled)

Figma mentions come through email notifications. If the Gmail MCP is available, search for Figma notification emails and extract mention details.

---

## Phase 3: Analyze

Get all unanalyzed pings and process them using the analysis prompt from `references/analysis-prompt.md`.

```python
unanalyzed = config.get_unanalyzed_pings()
if not unanalyzed:
    print("No new pings to analyze.")
```

For each ping, read the analysis prompt and substitute variables:
- `{USER_NAME}` → config.get("user.name")
- `{USER_CONTEXT}` → config.get_user_context()

Then analyze the ping content to determine:

| Field | Description |
|-------|-------------|
| **title** | `{Author Name}: {5-7 word action description}` |
| **summary** | What they want from you and what you need to do |
| **original_quote** | The exact text they sent (for blockquote) |
| **suggested_action** | One of: Acknowledge, Review, Reply, Decide, Delegate |
| **action_summary** | Single sentence of what to do |
| **priority** | 0-4 (see analysis-prompt.md for rules) |
| **specific_guidance** | Additional context if needed |
| **other_participants** | Other people involved in the thread |
| **source_description** | Formatted source (e.g., "Slack: #woo-design") |

Store the analysis:
```python
config.update_ping_analysis(ping_id, {
    "title": title,
    "summary": summary,
    "original_quote": original_quote,
    "suggested_action": action,
    "action_summary": action_summary,
    "priority": priority,
    "specific_guidance": guidance,
    "other_participants": other_participants,
    "source_description": source_description,
    "analyzed_at": datetime.now().isoformat()
})
```

---

## Phase 4: Sync to Linear

Sync analyzed pings to Linear using the format from `references/linear-template.md`.

**IMPORTANT**: Only sync P1 (Urgent) and P2 (High) priority pings. P3/P4 pings are analyzed but not synced to Linear.

### Filter pings for sync

```python
analyzed_pings = config.get_analyzed_pings()
pings_to_sync = [p for p in analyzed_pings if p["analysis"]["priority"] in [1, 2]]
skipped_low_priority = len(analyzed_pings) - len(pings_to_sync)
```

### For each ping to sync:

**Step 1: Check for duplicates**

```python
# Fast URL-based check
permalink = ping["metadata"].get("permalink")
if permalink and config.is_url_synced(permalink):
    continue  # Already synced

# Thread-based check
existing_issue = config.get_thread_linear_issue(ping["thread_id"])
```

**Step 2: If thread has existing issue** - Add a follow-up comment (don't modify the original issue):

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="add-comment",
    params={
        "issueId": existing_issue,
        "body": format_followup_comment(analysis, ping)
    }
)
```

If the follow-up ping has higher priority than the original issue, also update the issue priority:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="update-issue",
    params={
        "id": existing_issue,
        "priority": analysis["priority"]
    }
)
```

**Step 3: If no existing issue** - Create a new one with ALL required fields:

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="create-issue",
    params={
        "teamId": config.get("linear.team_id"),
        "title": analysis["title"],
        "description": format_description(analysis, ping),
        "stateId": get_triage_state_id(),  # Always "Triage" status
        "assigneeId": config.get("linear.user_id"),  # Always assigned to user
        "priority": analysis["priority"],  # 1 or 2
        "createdAt": ping["timestamp"]  # Match original ping date
    }
)
```

**Step 4: Link the issue to the ping**

```python
config.link_linear_issue(ping_id, issue["id"])
# Note: link_linear_issue automatically marks the URL as synced
```

### Pagination Note

When querying existing issues for deduplication, the Linear API returns max 100 results. Use the `synced_urls` list in config for faster deduplication. If you need to query Linear, use pagination cursors.

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
- Priority 3 (Normal): N (not synced)
- Priority 4 (Low): N (not synced)

**Synced to Linear:**
- Created X new issues
- Added Y comments to existing threads
- Auto-closed Z responded issues
- Skipped W low-priority pings (P3/P4)

**Next:** [Open your Linear triage inbox →](https://linear.app/team/{team_id}/triage)
```

If no new pings were found:

> You're all caught up! No new mentions since your last triage.

---

## Helper: Format Description

```python
def format_description(analysis: dict, ping: dict) -> str:
    """Format Linear issue description from analysis and ping data."""
    from datetime import datetime

    # Format source based on platform
    if ping["platform"] == "slack":
        source = f"Slack: #{ping['metadata'].get('channel_name', 'unknown')}"
    elif ping["platform"] == "p2":
        site = ping["metadata"].get("site_name", "unknown")
        post = ping["metadata"].get("post_title", "")
        source = f"P2: {site}" + (f" / {post}" if post else "")
    else:
        source = ping["platform"].title()

    # Format relative date
    try:
        ping_date = datetime.fromisoformat(ping["timestamp"].replace("Z", "+00:00"))
        now = datetime.now(ping_date.tzinfo) if ping_date.tzinfo else datetime.now()
        days_ago = (now - ping_date).days
        if days_ago == 0:
            relative_date = "today"
        elif days_ago == 1:
            relative_date = "yesterday"
        else:
            relative_date = f"{days_ago} days ago"
    except:
        relative_date = "recently"

    # Build description
    description = f"""{analysis['summary']}

> "{analysis['original_quote']}"

---

**Action:** {analysis['suggested_action']}

{analysis['action_summary']}

---

- Author: {ping['author']}
- Source: {source}
- Also involved: {analysis.get('other_participants', 'None')}
- Date: {relative_date}
- [View in {ping['platform'].title()}]({ping['metadata'].get('permalink', '#')})"""

    return description
```

## Helper: Format Follow-up Comment

```python
def format_followup_comment(analysis: dict, ping: dict, priority_changed: bool = False) -> str:
    """Format a follow-up comment for an existing Linear issue."""
    from datetime import datetime

    # Format relative date
    try:
        ping_date = datetime.fromisoformat(ping["timestamp"].replace("Z", "+00:00"))
        now = datetime.now(ping_date.tzinfo) if ping_date.tzinfo else datetime.now()
        days_ago = (now - ping_date).days
        if days_ago == 0:
            relative_date = "today"
        elif days_ago == 1:
            relative_date = "yesterday"
        else:
            relative_date = f"{days_ago} days ago"
    except:
        relative_date = "recently"

    # Build comment
    comment = f"""**Follow-up from {ping['author']}** ({relative_date})

{analysis['summary']}

> "{analysis['original_quote']}"

**Action:** {analysis['suggested_action']}

{analysis['action_summary']}

[View in {ping['platform'].title()}]({ping['metadata'].get('permalink', '#')})"""

    # Add priority change note if applicable
    if priority_changed:
        priority_label = {1: "Urgent", 2: "High"}.get(analysis["priority"], "Updated")
        comment += f"\n\n---\n*Priority updated to {priority_label}*"

    return comment
```

---

## Error Handling

If something fails during execution:

1. **MCP provider won't load**: Tell user which provider failed, suggest checking MCP connections
2. **No config found**: Direct to `/setup`
3. **Linear API error**: Show the error, suggest checking team ID in config
4. **Platform fetch fails**: Continue with other platforms, note which one failed
5. **Write permission error**: Config changes logged but may not persist - warn user

Never expose technical details like stack traces or raw API errors. Translate to user-friendly messages.

---

## References

- `references/analysis-prompt.md` - Complete analysis logic and output format
- `references/linear-template.md` - Linear issue formatting and threading strategy
- `references/platform-guide.md` - Platform-specific MCP tool details
