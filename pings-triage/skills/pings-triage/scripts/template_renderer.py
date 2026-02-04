#!/usr/bin/env python3
"""
Template Renderer for Pings Triage Plugin

Deterministic formatting functions for Linear issue titles, descriptions,
and comments. This module ensures consistent output regardless of how
Claude interprets the analysis prompt.

All template composition happens here - Claude provides the structured
data fields, and this module handles the formatting.
"""

from datetime import datetime
from typing import Dict, Optional


def format_title(analysis: dict) -> str:
    """
    Format Linear issue title from analysis fields.

    Always returns '{Author}: {action}' format, ensuring consistency
    across all pings regardless of platform.

    Args:
        analysis: Dict containing 'author_name' and 'action_summary_short'

    Returns:
        Formatted title string like "Elizabeth Bott: Review Customers design by Friday"
    """
    author = analysis.get("author_name", "Unknown")
    action = analysis.get("action_summary_short", "Action needed")

    return f"{author}: {action}"


def format_description(analysis: dict, ping: dict) -> str:
    """
    Format Linear issue description from analysis and ping data.

    Uses a strict template with placeholders filled from structured data.
    The description includes summary, quoted text, action details, and metadata.

    Args:
        analysis: Dict containing summary, original_quote, suggested_action,
                  action_summary, other_participants
        ping: Dict containing author, platform, timestamp, metadata

    Returns:
        Formatted markdown description string
    """
    # Format source based on platform
    source = _format_source(ping)

    # Format relative date
    relative_date = _format_relative_date(ping.get("timestamp"))

    # Get values with defaults
    summary = analysis.get("summary", "No summary available")
    original_quote = analysis.get("original_quote", "")
    suggested_action = analysis.get("suggested_action", "Review")
    action_summary = analysis.get("action_summary", "Review and respond")
    other_participants = analysis.get("other_participants", "None")
    author = ping.get("author", "Unknown")
    platform = ping.get("platform", "unknown").title()
    permalink = ping.get("metadata", {}).get("permalink", "#")

    # Build description using strict template
    description = f"""{summary}

> "{original_quote}"

---

**Action:** {suggested_action}

{action_summary}

---

- Author: {author}
- Source: {source}
- Also involved: {other_participants}
- Date: {relative_date}
- [View in {platform}]({permalink})"""

    return description


def format_followup_comment(
    analysis: dict,
    ping: dict,
    priority_changed: bool = False
) -> str:
    """
    Format a follow-up comment for an existing Linear issue.

    Used when a new ping arrives for a thread that already has a Linear issue.
    The comment captures the new information without modifying the original issue.

    Args:
        analysis: Dict containing summary, original_quote, suggested_action,
                  action_summary, priority
        ping: Dict containing author, platform, timestamp, metadata
        priority_changed: Whether to include a priority update note

    Returns:
        Formatted markdown comment string
    """
    # Format relative date
    relative_date = _format_relative_date(ping.get("timestamp"))

    # Get values with defaults
    author = ping.get("author", "Unknown")
    summary = analysis.get("summary", "Follow-up received")
    original_quote = analysis.get("original_quote", "")
    suggested_action = analysis.get("suggested_action", "Review")
    action_summary = analysis.get("action_summary", "Review and respond")
    platform = ping.get("platform", "unknown").title()
    permalink = ping.get("metadata", {}).get("permalink", "#")

    # Build comment using strict template
    comment = f"""**Follow-up from {author}** ({relative_date})

{summary}

> "{original_quote}"

**Action:** {suggested_action}

{action_summary}

[View in {platform}]({permalink})"""

    # Add priority change note if applicable
    if priority_changed:
        priority = analysis.get("priority", 0)
        priority_label = {1: "Urgent", 2: "High"}.get(priority, "Updated")
        comment += f"\n\n---\n*Priority updated to {priority_label}*"

    return comment


def _format_source(ping: dict) -> str:
    """
    Format source location string based on platform.

    Args:
        ping: Dict containing platform and metadata

    Returns:
        Formatted source string like "Slack: #channel" or "P2: site / post"
    """
    platform = ping.get("platform", "unknown")
    metadata = ping.get("metadata", {})

    if platform == "slack":
        channel_name = metadata.get("channel_name", "unknown")
        return f"Slack: #{channel_name}"
    elif platform == "p2":
        site = metadata.get("site_name", "unknown")
        post = metadata.get("post_title", "")
        if post:
            return f"P2: {site} / {post}"
        return f"P2: {site}"
    elif platform == "figma":
        file_name = metadata.get("file_name", "unknown")
        return f"Figma: {file_name}"
    else:
        return platform.title()


def _format_relative_date(timestamp: Optional[str]) -> str:
    """
    Format a timestamp as a relative date string.

    Args:
        timestamp: ISO format timestamp string, or None

    Returns:
        Relative date string like "today", "yesterday", or "3 days ago"
    """
    if not timestamp:
        return "recently"

    try:
        # Handle both formats: with and without timezone
        if timestamp.endswith("Z"):
            timestamp = timestamp.replace("Z", "+00:00")

        ping_date = datetime.fromisoformat(timestamp)

        # Get current time in same timezone if possible
        if ping_date.tzinfo:
            now = datetime.now(ping_date.tzinfo)
        else:
            now = datetime.now()

        days_ago = (now - ping_date).days

        if days_ago == 0:
            return "today"
        elif days_ago == 1:
            return "yesterday"
        else:
            return f"{days_ago} days ago"

    except (ValueError, TypeError):
        return "recently"


def validate_analysis(analysis: dict) -> tuple[bool, list[str]]:
    """
    Validate that analysis contains all required fields.

    Args:
        analysis: Dict to validate

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    required_fields = [
        "author_name",
        "action_summary_short",
        "summary",
        "original_quote",
        "suggested_action",
        "action_summary",
        "priority",
    ]

    missing = [field for field in required_fields if field not in analysis]

    return len(missing) == 0, missing


if __name__ == "__main__":
    # Example usage and testing
    print("Testing template_renderer...")

    sample_analysis = {
        "author_name": "Elizabeth Bott",
        "action_summary_short": "Review Customers design by Friday",
        "summary": "Elizabeth wants you to review the new Customers page design.",
        "original_quote": "Hey @james, can you take a look at this Customers design?",
        "suggested_action": "Review",
        "action_summary": "Review the Figma design and share feedback before Friday",
        "priority": 2,
        "other_participants": "None",
        "source_description": "Slack: #woo-design"
    }

    sample_ping = {
        "author": "Elizabeth Bott",
        "platform": "slack",
        "timestamp": "2024-01-15T14:30:00Z",
        "metadata": {
            "channel_name": "woo-design",
            "permalink": "https://automattic.slack.com/archives/C12345/p1234567890"
        }
    }

    print(f"\nTitle: {format_title(sample_analysis)}")
    print(f"\nDescription:\n{format_description(sample_analysis, sample_ping)}")
    print(f"\nValidation: {validate_analysis(sample_analysis)}")
