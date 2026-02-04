---
name: pings
description: Smart triage - collects, analyzes, and syncs your pings in one command
skill: pings-triage
---

# Pings

The smart triage command that does everything: collects your mentions from Slack and P2, analyzes what needs your attention, and syncs to Linear.

## What it does

1. **Collects** new mentions from your enabled platforms (since last run, or last 30 days on first run)
2. **Analyzes** each ping to determine what's needed (Reply, Review, Acknowledge, Decide, Delegate) and priority
3. **Syncs** to Linear - creates issues, updates threads, auto-closes responded items

## Examples

- "Check my pings"
- "Triage my mentions"
- "What notifications do I have?"
- `/pings`

## First time?

If you haven't configured yet, run `/setup` first to:
- Connect your Linear team
- Set your role and context
- Choose which platforms to monitor

## Output

You'll see a summary like:

```
Collected: 5 Slack, 2 P2
Analyzed: 3 to reply, 2 to review, 2 FYI
Synced: 7 Linear issues created

Open your triage inbox →
```

If you're all caught up:

```
No new pings since your last triage. You're caught up!
```
