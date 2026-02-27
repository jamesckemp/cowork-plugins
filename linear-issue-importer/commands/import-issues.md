---
argument-hint: Path to document (transcript, bug list, meeting notes)
---

# /import-issues

Extract issues from a document and import them into Linear.

## Mode Requirement

This command requires execute mode. If plan mode is active, call ExitPlanMode immediately. Write a single-line plan: "Run /import-issues as requested." Do not create a detailed implementation plan — the skill defines its own workflow.

Use skill: linear-issue-importer

The user wants to extract issues from the following file and import them into Linear:

**File:** `$ARGUMENTS`

**Do NOT pre-process the file.** If the file contents are already visible in this conversation (via @ reference), ignore them until the skill workflow reaches Step 1a. Do not summarize, extract quotes, or analyze the file before following the skill's Pre-Flight Check and workflow steps in order.

Follow the full workflow defined in the skill (Step 0 through Step 8). Start with Step 0 (gather source context), then proceed through all remaining steps.
