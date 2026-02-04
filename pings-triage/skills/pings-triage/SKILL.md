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

> **Session Folders for Outputs**
>
> Reports, exports, and other output files should go in session folders at the working directory root.
> Session folders use the format `YYYY-MM-DD_HHMM` (e.g., `2024-01-15_1430/`).
>
> ```python
> # Get path for a file in the current session folder
> report_path = config.get_session_file("triage_summary.md")
> export_path = config.get_session_file("batch_issues.json")
> ```
>
> The session timestamp is set once per ConfigManager instance, so all files from one triage run
> go in the same folder. Config stays in `.pings-triage/config.json` (unchanged).

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

**IMPORTANT**: The analysis must return pure JSON (no markdown, no explanation). The response must match the schema in `references/analysis-schema.json`.

| Field | Description |
|-------|-------------|
| **author_name** | Full name of the person who sent the ping |
| **action_summary_short** | 5-7 word action phrase (no author name, no [P2] prefix) |
| **summary** | What they want from you and what you need to do |
| **original_quote** | The exact text they sent (for blockquote) |
| **suggested_action** | One of: Acknowledge, Review, Reply, Decide, Delegate |
| **action_summary** | Single sentence of what to do |
| **priority** | 0-4 (see analysis-prompt.md for rules) |
| **specific_guidance** | Additional context if needed |
| **other_participants** | Other people involved in the thread |
| **source_description** | Formatted source (e.g., "Slack: #woo-design") |

### JSON Validation

After receiving the analysis response, validate and parse it:

```python
import json
from scripts.template_renderer import validate_analysis

try:
    analysis = json.loads(response)
except json.JSONDecodeError as e:
    print(f"Analysis returned invalid JSON for ping {ping_id}. Skipping.")
    continue

# Validate required fields
is_valid, missing = validate_analysis(analysis)
if not is_valid:
    print(f"Analysis missing required fields for ping {ping_id}: {missing}. Skipping.")
    continue
```

Store the analysis:
```python
from datetime import datetime

config.update_ping_analysis(ping_id, {
    "author_name": analysis["author_name"],
    "action_summary_short": analysis["action_summary_short"],
    "summary": analysis["summary"],
    "original_quote": analysis["original_quote"],
    "suggested_action": analysis["suggested_action"],
    "action_summary": analysis["action_summary"],
    "priority": analysis["priority"],
    "specific_guidance": analysis.get("specific_guidance", ""),
    "other_participants": analysis.get("other_participants", "None"),
    "source_description": analysis.get("source_description", ""),
    "analyzed_at": datetime.now().isoformat()
})
```

---

## Phase 4: Sync to Linear

Sync analyzed pings to Linear using the template renderer for consistent formatting.

**IMPORTANT**: Only sync P1 (Urgent) and P2 (High) priority pings. P3/P4 pings are analyzed but not synced to Linear.

### Import template renderer

```python
from scripts.template_renderer import format_title, format_description, format_followup_comment
```

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

```python
# Use template renderer for consistent comment formatting
comment_body = format_followup_comment(ping["analysis"], ping)
```

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="add-comment",
    params={
        "issueId": existing_issue,
        "body": comment_body
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
        "priority": ping["analysis"]["priority"]
    }
)
```

**Step 3: If no existing issue** - Create a new one with ALL required fields:

```python
# Use template renderer for consistent title and description formatting
# Title is composed from author_name + action_summary_short
title = format_title(ping["analysis"])
description = format_description(ping["analysis"], ping)
```

```
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="create-issue",
    params={
        "teamId": config.get("linear.team_id"),
        "title": title,  # Guaranteed format: "{Author}: {action}"
        "description": description,  # Consistent markdown template
        "stateId": get_triage_state_id(),  # Always "Triage" status
        "assigneeId": config.get("linear.user_id"),  # Always assigned to user
        "priority": ping["analysis"]["priority"],  # 1 or 2
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

- `references/analysis-prompt.md` - Complete analysis logic and JSON output format
- `references/analysis-schema.json` - JSON schema for required analysis fields
- `references/platform-guide.md` - Platform-specific MCP tool details
- `scripts/template_renderer.py` - Deterministic formatting functions for Linear issues
