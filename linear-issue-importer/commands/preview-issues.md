---
argument-hint: Path to document (transcript, bug list, meeting notes)
---

# /preview-issues

Extract and preview issues from a document WITHOUT creating them in Linear. Use this to verify extraction quality before running `/import-issues`.

## Mode Requirement

This command requires execute mode. If plan mode is active, call ExitPlanMode immediately. Write a single-line plan: "Run /preview-issues as requested." Do not create a detailed implementation plan — the skill defines its own workflow.

Use skill: linear-issue-importer

The user wants to **preview only** — do NOT create any Linear issues.

**File:** `$ARGUMENTS`

**Do NOT pre-process the file.** If the file contents are already visible in this conversation (via @ reference), ignore them until the skill workflow reaches Step 1a. Do not summarize, extract quotes, or analyze the file before following the skill's Pre-Flight Check and workflow steps in order.

Follow Step 0 (Gather Source Context) then Steps 1–6 of the workflow (Read & Extract, Internal Dedup, Build Working Document, Gather Linear Configuration, Linear Duplicate Search & Resolution, User Confirms Issues). Stop after Step 6. Do NOT proceed to Step 7 (import) or Step 8 (summary).

After presenting the confirmed list, tell the user:

> This is a preview. No issues were created in Linear. When you're ready, run `/import-issues <path>` to create them.
