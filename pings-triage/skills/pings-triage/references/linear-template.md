# Linear Issue Template

This document defines how ping triage issues are formatted in Linear.

## Issue Creation Rules

### What Gets Synced

**Only P1 (Urgent) and P2 (High) priority pings are synced to Linear.** P3 (Normal) and P4 (Low) pings are analyzed and tracked locally but do not create Linear issues.

### Deduplication Strategy

Before creating an issue, check if it already exists:

1. **URL-based deduplication**: Check `config.is_url_synced(permalink)` for fast lookup
2. **Thread-based deduplication**: Check `config.get_thread_linear_issue(thread_id)` to see if the thread already has an issue
3. **If existing issue found**: Add a comment instead of creating a duplicate

### Pagination Note

When querying existing issues (for deduplication or updates), the Linear API returns max 100 issues per request. For users with large triage inboxes:
- Use `first: 100` with pagination cursors
- Query by team + status to narrow results
- The `synced_urls` list in config provides faster deduplication than API queries

## Issue Structure

### Team
- Use the configured team ID from user config
- **CRITICAL**: Never create issues in other teams to prevent exposing private information

### Title
- Format: `{Author Name}: {5-7 word action summary}`
- Focus on what needs to be DONE, not what was said
- Examples:
  - "Elizabeth Bott: Review Customers design by Friday"
  - "Laura Nelson: Decide on offline refunds scope"
  - "Cvetan Cvetanov: Acknowledge their response"

### Description

The description uses a structured format with blockquote, action section, and metadata:

```markdown
{Summary from analysis - what they want and what you need to do}

> "{Original quoted ping text}"

---

**Action:** {Suggested Action}

{Action summary sentence - the specific thing to do}

---

- Author: {Author Name} ({username if available})
- Source: {Platform}: {location}
- Also involved: {Other participants or "None"}
- Date: {Relative timestamp like "2 days ago"}
- [View in {Platform}]({permalink})
```

### Status
- **ALL new issues**: Set to "Triage" status (regardless of priority)
- Status comes from `config.get("linear.status_new")` which defaults to "Triage"
- Completed issues: "Done" (when ping has been responded to)

### Assignee
- **ALL issues**: Assigned to the user
- Use `config.get("linear.user_id")` to get the user's Linear ID
- If `user_id` is not set, call the Linear `me` API to get it on first run

### Priority
Maps directly from analysis priority (0-4 scale):
- 1 = Urgent (P1)
- 2 = High (P2)
- 3 = Normal (not synced)
- 4 = Low (not synced)
- 0 = None (not synced)

### Created At
- Set `createdAt` to match the ping's original timestamp
- This ensures Linear's timeline reflects when you were actually pinged, not when you ran triage

### Labels
- Each ping gets a unique label with format: `ping-{hash}`
- The hash is derived from the message content and platform
- Labels help track which Linear issue corresponds to which ping

## Issue Creation Parameters

When creating an issue via the Linear MCP:

```python
mcp__context-a8c__context-a8c-execute-tool(
    provider="linear",
    tool="create-issue",
    params={
        "teamId": config.get("linear.team_id"),
        "title": analysis["title"],
        "description": format_description(analysis, ping),
        "stateId": get_triage_state_id(),  # Always "Triage"
        "assigneeId": config.get("linear.user_id"),  # Always assigned
        "priority": analysis["priority"],  # 1 or 2 only
        "createdAt": ping["timestamp"]  # Match ping date
    }
)
```

## Example Issue

**Title**: Elizabeth Bott: Review Customers design by Friday

**Description**:
```markdown
Elizabeth wants you to review the new Customers page design and provide feedback before the Friday sync.

> "Hey @james, can you take a look at this Customers design? Would love your feedback before our Friday sync."

---

**Action:** Review

Review the Figma design and share feedback before Friday

---

- Author: Elizabeth Bott (@elizabeth)
- Source: Slack: #woo-design
- Also involved: None
- Date: 2 days ago
- [View in Slack](https://automattic.slack.com/archives/C12345/p1234567890)
```

**Status**: Triage
**Assignee**: James Kemp (jamesckemp)
**Priority**: 2 (High)
**Created At**: 2024-01-15T14:30:00Z (ping timestamp)
**Labels**: ping-0ac94172-e452-4...3d-16bf75fd6942

## Thread Handling

When multiple pings belong to the same conversation thread, keep a **single Linear issue** and add follow-up messages as **comments**. This preserves the timeline of events and keeps all context together.

### How It Works

1. **First ping in thread** → Creates a new Linear issue with the full template
2. **Subsequent pings in same thread** → Add a comment to the existing issue (don't modify the original description)

The original issue description stays unchanged - it captures the initial ping. Comments capture the thread's evolution over time.

### Follow-up Comment Template

When a new ping arrives for an existing thread, add a comment using this format:

```markdown
**Follow-up from {Author}** ({relative_date})

{Summary of what they're saying/asking}

> "{Original quoted text}"

**Action:** {Suggested Action}

{Action summary}

[View in {Platform}]({permalink})
```

### Example Thread Flow

**Original Issue** (created from first ping):
> Elizabeth Bott: Review Customers design by Friday
>
> Elizabeth wants you to review the new Customers page design...

**Comment 1** (added when Elizabeth follows up):
```markdown
**Follow-up from Elizabeth Bott** (yesterday)

Elizabeth is checking in on the design review and asking if you have any initial thoughts.

> "Hey @james, just checking in - any initial thoughts on the design? Happy to jump on a call if easier."

**Action:** Reply

Respond with initial feedback or schedule a call

[View in Slack](https://automattic.slack.com/archives/C12345/p1234567891)
```

**Comment 2** (added when someone else joins the thread):
```markdown
**Follow-up from Laura Nelson** (today)

Laura is offering to help with the review if you're busy this week.

> "@james I can take a first pass at the design feedback if you're swamped - just let me know"

**Action:** Decide

Decide whether to delegate the initial review to Laura

[View in Slack](https://automattic.slack.com/archives/C12345/p1234567892)
```

### Priority Updates

If a follow-up ping has higher priority than the original (e.g., someone is now blocked), update the issue's priority to match. Add a note in the comment:

```markdown
**Follow-up from Laura Nelson** (today)

Laura says the team is now blocked waiting on design feedback.

> "Hey @james - FYI we're blocked on this now, need to finalize by EOD"

**Action:** Review

Prioritize the design review - team is blocked

[View in Slack](https://automattic.slack.com/archives/C12345/p1234567893)

---
*Priority updated from High to Urgent - team is blocked*
```

## Auto-closing Rules

Issues should be automatically closed (moved to "Done") when:
1. The user has replied to the message on the original platform
2. The user has reacted to the message with an emoji/like
3. The user manually marks the ping as handled
4. The suggested action was "Acknowledge" and sufficient time has passed (e.g., 24 hours)

When auto-closing, add a comment to the issue noting why it was closed:
- "Automatically closed: Reply detected on {platform}"
- "Automatically closed: Reaction added"
- "Automatically closed: Marked as handled"

## Formatting Helpers

### Issue Description (for new issues)

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

### Follow-up Comment (for existing threads)

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
