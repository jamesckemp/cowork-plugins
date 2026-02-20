---
argument-hint: Path to document (transcript, bug list, meeting notes)
---

# /preview-issues

Extract and preview issues from a document WITHOUT creating them in Linear. Use this to verify extraction quality before running `/import-issues`.

Use skill: linear-issue-importer

The user wants to **preview only** — do NOT create any Linear issues.

**File:** `$ARGUMENTS`

Follow Steps 1–6 of the workflow (Read & Extract, Internal Dedup, Build Working Document, Gather Linear Configuration, Linear Duplicate Search & Resolution, User Confirms Issues). Stop after Step 6. Do NOT proceed to Step 7 (import) or Step 8 (summary).

After presenting the confirmed list, tell the user:

> This is a preview. No issues were created in Linear. When you're ready, run `/import-issues <path>` to create them.
