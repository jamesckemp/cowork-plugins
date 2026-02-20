# Extraction Patterns

How to identify and extract issues from different document types.

## Document Type Detection

Check these in order — use the first match:

| Type | Detection Signal |
|------|-----------------|
| Granola JSON | Top-level `id`, `title`, `notes_markdown`, and `transcript` array |
| Granola Obsidian Note | YAML frontmatter containing `granola_id` and `granola_url` |
| Markdown Bug List | `##` category headings with `###` individual items; "Bug:", "UX:", "Task:" prefixes |
| Raw Transcript | Speaker labels (e.g., "James:", "Speaker 1:"), timestamps, conversational text |
| General Document | Fallback — structured lists, headings, action-oriented language |

---

## Granola JSON

Granola exports meeting data as JSON with this structure:

### Top-level fields
- `id` — unique meeting identifier
- `title` — meeting title
- `created_at` — ISO-8601 timestamp
- `notes_markdown` — AI-generated meeting notes in markdown
- `transcript[]` — array of utterances
- `google_calendar_event` (optional) — includes `attendees[]` with `name`, `email`, `title`
- `people` (optional) — participant details object

### Transcript format
Each utterance in `transcript[]` has:
- `start_timestamp` / `end_timestamp` — ISO-8601 timestamps
- `source` — `"microphone"` (recorder's voice) or `"system"` (remote participants)
- `text` — spoken words

### Extraction approach
1. Parse `notes_markdown` first — it contains structured summaries with headings and bullets
2. Scan `transcript[]` for additional issues not captured in notes:
   - Look for problem/decision/request language (see Signal Words below)
   - Group nearby utterances into coherent statements
3. Calculate human-readable timestamps as MM:SS offset from the first transcript entry's `start_timestamp`
4. For each identified issue, include:
   - The exact quote from transcript
   - The timestamp range (e.g., "12:34–13:01")
   - Who raised it (from speaker identification or `source` field)

### Source link
Use `id` to construct: `https://notes.granola.ai/d/{id}`

---

## Granola Obsidian Note

Exported Granola notes saved to Obsidian have:

### YAML frontmatter
```yaml
---
granola_id: <uuid>
title: <meeting title>
granola_url: https://notes.granola.ai/d/<uuid>
created_at: <ISO-8601>
updated_at: <ISO-8601>
tags:
  - person/<name>
  - person/<name>
---
```

### Body structure
- `###` headings for topic sections
- Bullet points (`-`) with details under each heading
- Nested bullets for sub-points

### Extraction approach
1. Each `###` heading is a topic — scan bullets underneath for actionable items
2. Look for:
   - Problems described ("X is broken", "X doesn't work", "issue with X")
   - Decisions made ("decided to", "agreed on", "will do X")
   - Action items ("need to", "should", "TODO", "follow up on")
   - Blockers ("blocked by", "waiting on", "depends on")
3. Use `granola_url` from frontmatter as the source link
4. Use `tags` to identify participants (strip `person/` prefix)

---

## Markdown Bug List

Structured bug documents with category groupings.

### Format
```markdown
## [Category Name]

### [Bug Title]

Bug: [Description]
[Additional context]

### [Another Bug]

UX: [Description]
```

### Extraction approach
1. `##` headings define categories — use as the issue category
2. `###` headings are individual bug titles
3. Text after prefixes contains the description:
   - `Bug:` — defect, something broken
   - `UX:` — usability issue, confusing flow
   - `Task:` — work item, improvement needed
   - `Decision:` / `Decision/task:` — pending decision or hybrid
4. All remaining text until the next `###` is additional context
5. If the bug title already has a Linear link (e.g., `[TEAM-1234](url)`), it's already been created — skip it

---

## Raw Transcript

Meeting transcripts with speaker labels.

### Common formats
```
[00:12:34] James: We need to fix the checkout flow
James (12:34): The checkout is broken for guest users
Speaker 1: Has anyone looked at the payment timeout?
```

### Extraction approach
1. Identify speaker labels (Name:, Speaker N:, or bracketed names)
2. Group consecutive statements by the same speaker or on the same topic
3. Look for Signal Words (below) to identify issues
4. Extract timestamp if present — normalize to MM:SS format
5. Capture the full statement as the source quote

---

## General Document

Fallback for any structured document.

### Extraction approach
1. Scan for headings (`#`, `##`, `###`) — each may contain a topic with issues
2. Look for:
   - Numbered or bulleted lists with action items
   - Bold or emphasized text highlighting problems
   - Checkbox items (`- [ ]` or `- [x]`)
   - Tables with status columns
3. Apply Signal Words (below) to identify actionable items
4. Group by heading hierarchy for categories

---

## Signal Words

Use these to identify issues and suggest priority:

### Problem indicators (likely bugs)
- "broken", "doesn't work", "fails", "error", "crash", "bug", "issue", "wrong"
- "missing", "not showing", "disappears", "lost", "corrupt"
- "inconsistent", "mismatch", "out of sync", "stale"

### Action indicators (likely tasks)
- "need to", "should", "must", "TODO", "follow up", "action item"
- "implement", "add", "create", "build", "set up", "configure"
- "fix", "resolve", "address", "handle", "update", "change"

### Request indicators (likely feature requests)
- "would be nice", "it would help", "can we", "what if"
- "feature request", "enhancement", "improvement", "suggestion"
- "users want", "customers need", "feedback"

### Decision indicators
- "decided", "agreed", "will do", "going with", "approved"
- "rejected", "won't do", "deferred", "postponed", "revisit"

## Priority Signal Words

| Priority | Signal Words |
|----------|-------------|
| Urgent | "critical", "blocker", "P0", "showstopper", "ASAP", "urgent", "emergency" |
| High | "important", "P1", "high priority", "must have", "regression", "data loss" |
| Medium | "should fix", "P2", "moderate", "normal", "soon" |
| Low | "nice to have", "P3", "low priority", "minor", "cosmetic", "someday" |
| None (default) | No signal words detected — let user decide |
