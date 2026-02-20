---
description: Extract issues from documents and import them into Linear
user-invocable: false
---

# Linear Issue Importer

Extract issues from any document and import them into Linear.

## Invocation

- `/import-issues <path/to/file>` — full workflow: extract, configure, create in Linear
- `/preview-issues <path/to/file>` — dry run: extract and configure only, nothing created in Linear

For `/preview-issues`, run Steps 1–4 only, then stop. Do not create any issues.

## Required References

**Read these files before starting the workflow:**

1. `references/extraction-patterns.md` — document type detection and issue extraction rules
2. `references/issue-template.md` — **required** description templates (Bug Report, Action Item, Feature Request)

These files are NOT auto-loaded. You must read them explicitly. Issue descriptions that don't follow the templates will be rejected by the user.

## Workflow

### Step 1: Read & Extract Issues

1. Read the file from the provided path
2. Detect the document type:
   - **Granola JSON** — top-level `id`, `title`, `notes_markdown`, `transcript[]` fields
   - **Granola Obsidian note** — YAML frontmatter with `granola_id`, `title`, `granola_url`, `tags`; body uses `###` headings + bullet points
   - **Markdown bug list** — `##` category headings, `###` individual bugs, prefixes like "Bug:", "UX:", "Task:"
   - **Raw transcript** — speaker labels, timestamps, conversational text
   - **General document** — fallback: structured lists, action-oriented language
3. Extract issues using patterns from `references/extraction-patterns.md`
4. For each extracted issue, capture:
   - **Title** — concise, action-oriented summary
   - **Description** — full context from the source
   - **Source quote** — exact text from the document
   - **Timestamp** — if available (transcript time offset or document date)
   - **Suggested priority** — based on signal words (see extraction-patterns.md)
   - **Category** — functional grouping (e.g., "Onboarding", "Payments", "Design")
   - **Type** — bug, task, or feature request (determines which description template to use — see `references/issue-template.md`)

### Step 2: Build Working Document

1. Present extracted issues as a numbered list:
   ```
   ## Extracted Issues (N found)

   ### 1. [Title]
   - Type: Bug / Task / Feature Request
   - Priority: Urgent / High / Medium / Low
   - Category: [functional area]
   - Source: "[exact quote]"
   ```
2. If no issues were found, use `AskUserQuestion` to ask what to look for:
   - Bugs and defects
   - Action items and tasks
   - Feature requests
   - All of the above
3. **REQUIRED:** Format each issue's description using the matching template from `references/issue-template.md`:
   - Bug → Bug Report template
   - Task → Action Item / Task template
   - Feature Request → Feature Request template

   Omit template sections that have no meaningful content. Never use freeform descriptions.

### Step 3: Gather Linear Configuration

Use `AskUserQuestion` to collect Linear settings. Fetch real data from Linear MCP to populate choices.

1. **Team** — call `mcp__claude_ai_Linear__list_teams` and present options
2. **Labels** — call `mcp__claude_ai_Linear__list_issue_labels` for the chosen team, then ask which labels to apply to all issues
3. **Project** — call `mcp__claude_ai_Linear__list_projects` for the chosen team and ask which project to assign issues to (or "None")
4. **Assignee** — ask if the user wants to assign issues to someone; if yes, call `mcp__claude_ai_Linear__list_users`
5. **Parent issue** — ask if issues should be sub-issues of a parent (user provides identifier or UUID)
6. **Status** — call `mcp__claude_ai_Linear__list_issue_statuses` for the chosen team if user wants a non-default status

Present defaults clearly. Allow the user to set per-issue overrides (e.g., different labels or parent for specific issues).

### Step 4: User Confirms Issues

Present the final list with all Linear configuration applied:

```
## Ready to Import (N issues)

### 1. [Title]
- Team: [team name]
- Labels: [label1, label2, ...]
- Parent: [parent identifier] (if set)
- Assignee: [name] (if set)
- Description preview: [first 2 lines]

### 2. [Title]
...
```

Ask user to confirm. They can:
- **Approve all** — proceed to import
- **Remove specific issues** — by number
- **Edit titles or descriptions** — for specific issues
- **Change per-issue settings** — different labels, parent, etc.

**Do not proceed until the user explicitly confirms.**

### Step 5: Duplicate Check & Import

**Important — UUID tracking:** Linear's triage automation can move issues between teams after creation, which changes the human-readable identifier (e.g., WOOPRD-1234 becomes WOOPLUG-567). The UUID never changes. Always track created issues by their UUID, not their identifier.

For each confirmed issue:

1. **Search for duplicates** using `mcp__claude_ai_Linear__list_issues`:
   ```
   list_issues({ team: "<team>", query: "<2-3 key terms from title>", limit: 5 })
   ```
2. **If potential duplicates found**, present them to the user:
   ```
   Issue "Fix checkout timeout" may duplicate:
   - TEAM-1234: "Checkout times out on large carts" (Open)
   - TEAM-1189: "Payment timeout handling" (Done)

   Options: Create anyway / Skip / Link as related
   ```
3. **Create confirmed issues** using `mcp__claude_ai_Linear__create_issue`. **REQUIRED:** Each issue description MUST use the template from `references/issue-template.md` matching its Type (Bug Report, Action Item, or Feature Request). Include the source attribution line. Do not use freeform descriptions.
4. **After each `create_issue` call, store the UUID** (`id` field) from the response — not just the `identifier`. The UUID is the only stable reference once triage automation runs.
5. **Never re-search by identifier to verify creation.** If `create_issue` returned a UUID, the issue exists. Searching by the old identifier after triage routing has moved it will return nothing, which is not a failure — do not re-create the issue.
6. **For 10+ issues**, suggest using parallel agents grouped by category to speed up creation. Use the same pattern as the CIAB batch workflow:
   - Group by category to minimize cross-agent duplicate risk
   - 2-3 agents per batch
   - Each agent searches for duplicates before creating
   - Wait for each batch to complete before starting the next

### Step 6: Generate Summary

**Before generating the summary**, re-fetch every created issue by UUID using `mcp__claude_ai_Linear__get_issue({ id: "<uuid>" })`. This is critical because triage automation may have:
- Moved the issue to a different team (changing its identifier)
- Changed the URL
- Assigned it to someone
- Changed its status

Use the **current** identifier and URL from the `get_issue` response in the summary, not the values from the original `create_issue` response.

Create a markdown summary with:

```markdown
## Linear Import Summary

**Source:** [file path]
**Team:** [team name] (at time of creation — triage may have moved issues)
**Date:** [today's date]
**Total extracted:** N | **Created:** N | **Skipped:** N | **Removed:** N

### Created Issues

| # | ID | Title | URL |
|---|-----|-------|-----|
| 1 | TEAM-XXXX | Title here | [link](url) |

### Skipped (Duplicates)

| # | Title | Existing Issue | Reason |
|---|-------|---------------|--------|
| 1 | Title here | TEAM-XXXX | Near duplicate |

### Removed by User

- Title of removed issue 1
- Title of removed issue 2
```

Present this summary to the user. Offer to save it as `linear-import-YYYY-MM-DD-{topic}.md` in the current directory, where `{topic}` is 2-3 lowercase hyphenated words summarising the import (e.g., `linear-import-2026-02-20-checkout-bugs.md`, `linear-import-2026-02-20-onboarding-tasks.md`).

## Reference Files

- `references/extraction-patterns.md` — how to parse each document type
- `references/issue-template.md` — description templates for bugs, tasks, and feature requests
- `references/linear-tools.md` — Linear MCP tool quick reference
