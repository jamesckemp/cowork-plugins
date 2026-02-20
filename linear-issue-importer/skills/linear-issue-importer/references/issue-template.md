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

[Source attribution line — see below]
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

[Source attribution line — see below]
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

[Source attribution line — see below]
```

### When to use
- A new capability was requested
- An improvement or enhancement was suggested
- Signal words: "would be nice", "can we", "feature request", "enhancement"

---

## Source Attribution Line

Always include a source attribution at the end of every issue description. Choose the appropriate format:

### From a Granola note (with URL)
```markdown
---

This issue was identified in [Meeting Title](granola_url)
```

### From a Granola transcript (with timestamp)
```markdown
---

This issue was identified in [Meeting Title](granola_url) (at ~MM:SS)

> "Exact quote from transcript"
```

### From a document (with file path)
```markdown
---

This issue was extracted from `filename.md`
```

### From a document with a known URL
```markdown
---

This issue was discovered during the [Document Title](url)
```

### Quoting the source
When an exact quote is available (especially from transcripts), include it as a blockquote after the attribution line:

```markdown
> "The checkout flow breaks completely when you try to use a gift card with a coupon"
```

This helps reviewers trace the issue back to the original discussion.
