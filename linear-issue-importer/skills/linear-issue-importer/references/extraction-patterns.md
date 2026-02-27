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

**Route by transcript size:**
- **200+ utterances** → Chunked pipeline (see SKILL.md Step 1c–1e)
- **<200 utterances** → Single-pass transcript-first (below)

**Single-pass transcript-first extraction:**
1. Extract issues from `transcript[]` first — this is the primary source:
   - Read conversational flow deeply, not just keyword-scanning
   - Look for problem/decision/request language (see Signal Words below)
   - Connect cause and effect across speakers and time gaps
   - Treat indirect language as potential issues ("that's weird", "something happened")
   - Watch for Visual Gap Indicators (see section below)
   - Group related utterances into coherent issues
2. Cross-reference against `notes_markdown` for enrichment:
   - Issue found in both transcript and notes → enrich with notes language
   - Issue found only in notes → add with "notes-only" note
   - Issue found only in transcript → keep as-is (this is the key scenario that transcript-first catches)
3. Calculate video-referenceable timestamps as offset from the first transcript entry's `start_timestamp`:
   - `video_time = utterance.start_timestamp - first_utterance.start_timestamp`
   - Format as `H:MM:SS` (e.g., `1:37:05`)
   - Bias earlier — raw calculation naturally produces timestamps a few seconds early, which is preferable (users arrive before the relevant moment, not after)
4. For each identified issue, include:
   - The exact quote from transcript
   - The video timestamp range (e.g., "0:12:34–0:13:01")
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

**Route by transcript length:**
- **300+ lines** → Chunked pipeline (see SKILL.md Step 1c–1e). If timestamps are parseable from text (e.g., `[00:12:34]`), prefer time-based chunking.
- **<300 lines** → Single-pass extraction (below)

**Single-pass extraction:**
1. Identify speaker labels (Name:, Speaker N:, or bracketed names)
2. Read conversational flow deeply — connect cause and effect across speakers and time gaps
3. Look for Signal Words (below) and Visual Gap Indicators (below) to identify issues
4. Extract timestamp if present — normalize to H:MM:SS format as video-referenceable offset
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

## Visual Gap Indicators

These patterns suggest the speaker is reacting to something they can see on screen but not describing verbally. Issues identified this way may need screenshot or video recording verification.

### Reactions without descriptions
- "That's not good", "Oh no", "Hmm", "What is that?"
- "Wait, what?", "That shouldn't be there", "Where did it go?"
- Exclamations followed by silence or topic change

### Vague visual assessments
- "That's quite terrible", "It's functional", "That looks off"
- "Not great", "It's fine I guess", "That's ugly"
- Qualitative judgments without specific details

### UI interaction + unexpected result
- "I can't anymore", "It won't let me", "Nothing happened"
- "Wait, I just did that and now...", "It disappeared"
- Actions described but outcomes implied ("I clicked save and... yeah")

### Speaker referencing what others can see
- "Can you see that?", "Do you see what I mean?"
- "Look at this", "See how it...", "Right there"
- Deictic references ("this", "that", "here") without antecedents

### Handling
Flag these as: `[Potential visual issue — may need screenshot/recording verification]`

Include the video timestamp so users can scrub to the moment and see what was on screen. These issues may be:
- Real bugs that are purely visual (e.g., white text on white background)
- UI/UX issues that are hard to describe verbally
- False positives — verify before creating Linear issues

---

## Priority Signal Words

| Priority | Signal Words |
|----------|-------------|
| Urgent | "critical", "blocker", "P0", "showstopper", "ASAP", "urgent", "emergency" |
| High | "important", "P1", "high priority", "must have", "regression", "data loss" |
| Medium | "should fix", "P2", "moderate", "normal", "soon" |
| Low | "nice to have", "P3", "low priority", "minor", "cosmetic", "someday" |
| None (default) | No signal words detected — let user decide |
