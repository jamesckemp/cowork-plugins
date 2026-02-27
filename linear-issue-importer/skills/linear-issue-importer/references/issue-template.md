# Issue Description Templates

Use the appropriate template based on the issue type. Fill in sections from the extracted content. Omit sections that have no meaningful content rather than leaving placeholders.

---

## Bug Report

```markdown
## Describe the bug

[Clear description of the defect — what is broken, where it occurs, and who is affected]

## Steps to reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected behavior

[What should happen when following the steps above]

## Actual behavior

[What actually happens — include error messages, incorrect values, or broken UI if known]

---

[Source attribution block — see below]
```

### When to use
- Something is broken, incorrect, or crashing
- Signal words: "broken", "doesn't work", "error", "bug", "wrong", "fails"

---

## Action Item / Task

```markdown
## Task

[Clear description of what needs to be done]

## Context

[Why this task matters — background, who raised it, what it unblocks]

## Acceptance criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

[Source attribution block — see below]
```

### When to use
- A decision was made and needs implementation
- An action item was assigned in a meeting
- Something needs to be built, configured, or changed
- Signal words: "need to", "should", "TODO", "action item", "implement"

---

## Feature Request

```markdown
## Description

[What the feature should do]

## Problem it solves

[The user problem or pain point this addresses]

## Suggested approach

[How it might be implemented, if discussed in the source document]

---

[Source attribution block — see below]
```

### When to use
- A new capability was requested
- An improvement or enhancement was suggested
- Signal words: "would be nice", "can we", "feature request", "enhancement"

---

## Source Attribution Block

Always include a source attribution block at the end of every issue description. The block is built from two parts:

1. **Source line** — always present. Identifies the meeting/document and date.
2. **Supplementary links** — only included if the user provided them during Step 0b (e.g., summary post, video recording, related docs).

### Format

```markdown
---
Source: [Meeting Title](url) — YYYY-MM-DD
[Summary post](url)
[Video recording](url)
```

Supplementary link lines are only included if the user provided them. If no supplementary links were provided, just the Source line appears:

```markdown
---
Source: [Meeting Title](url) — YYYY-MM-DD
```

### Source line variants

**From a Granola note or transcript (with URL):**
```markdown
Source: [Meeting Title](https://notes.granola.ai/d/{id}) — YYYY-MM-DD
```

**From a document (with file path, no URL):**
```markdown
Source: `filename.md` — YYYY-MM-DD
```

**From a document with a known URL:**
```markdown
Source: [Document Title](url) — YYYY-MM-DD
```

### Quoting the source

When an exact quote is available (especially from transcripts), include it as a blockquote within the issue description (not in the attribution block). Include video timestamps when available:

```markdown
> "The checkout flow breaks completely when you try to use a gift card with a coupon" (at 1:37:05 in recording)
```

Video timestamps use `H:MM:SS` format calculated as offset from the first transcript utterance. This helps reviewers trace the issue back to the original discussion and jump to the right moment in any recording.
