---
description: Extract issues from documents and import them into Linear
user-invocable: false
---

If plan mode is active, exit it now using ExitPlanMode before starting this workflow. All import commands run in execute mode.

**Important:** This skill definition is the authoritative process. Do not reference previous session outputs to learn how extraction was done before — those may reflect an older version of this skill or a different approach entirely. Always follow the steps defined here.

# Linear Issue Importer

Extract issues from any document and import them into Linear.

## Invocation

- `/import-issues <path/to/file>` — full workflow: extract, deduplicate, configure, create in Linear
- `/preview-issues <path/to/file>` — dry run: extract, deduplicate, configure only, nothing created in Linear

For `/preview-issues`, run Steps 0–6 only, then stop. Do not create any issues.

## Required References

**Read these files before starting the workflow:**

1. `references/extraction-patterns.md` — document type detection and issue extraction rules
2. `references/issue-template.md` — **required** description templates (Bug Report, Action Item, Feature Request)
3. `references/chunk-agent-prompt.md` — prompt template for chunk analysis agents (only needed for chunked pipeline)

These files are NOT auto-loaded. You must read them explicitly. Issue descriptions that don't follow the templates will be rejected by the user.

## Pre-Flight Check (MANDATORY)

Before doing ANY work on the source file, complete these steps in order:

1. **Read ALL reference files listed above.** Do not proceed until you have read extraction-patterns.md, issue-template.md, and chunk-agent-prompt.md.
2. **Detect the document type** (Step 1a) and **determine the routing** (Step 1b).
3. **Report the routing decision to the user** before starting extraction:
   > Document type: [type]
   > Utterance/line count: [N]
   > Routing: [Chunked pipeline (Steps 1c-1e) / Single-pass transcript-first / Single-pass structured]
   > [If chunked] Estimated chunks: ~N (5-min windows, 2-min overlap)

Do NOT begin extraction until the routing decision has been reported.

## Workflow

**Interactive steps that require user input — do not skip:**
- Step 0b — Ask for supplementary links
- Step 2 — Internal dedup resolution (if overlaps found)
- Step 4 — Linear configuration
- Step 5c — Duplicate resolution
- Step 6 — Final confirmation

### Step 0: Gather Source Context

Run this step once at the start. It produces metadata and a reusable attribution block embedded in every created issue.

#### Step 0a: Identify source metadata

After reading the file, extract:
- **Source title** — meeting title (from Granola JSON `title`, Obsidian frontmatter `title`, or filename)
- **Source date** — meeting/document date (from Granola JSON `created_at`, Obsidian frontmatter `created_at`, or file modification date)
- **Source link** — Granola URL (`https://notes.granola.ai/d/{id}`), Obsidian frontmatter `granola_url`, or file path if no URL available

#### Step 0b: Ask for supplementary links

Use `AskUserQuestion` to ask:

> Do you have any links to include in every issue? (e.g., summary post, video recording, related docs)

Options:
- **Yes, let me provide links** — collect one or more URLs with labels
- **No, continue without extra links** — proceed immediately

If the user provides links, store them as `supplementary_links[]` for use in issue descriptions.

#### Step 0c: Compose source attribution block

Build a reusable attribution block following the format in `references/issue-template.md`. This block is appended to every issue description:

```markdown
---
Source: [Meeting Title](url) — YYYY-MM-DD
[Summary post](url)
[Video recording](url)
```

Supplementary link lines are only included if the user provided them in Step 0b. If no links were provided, just the Source line appears.

### Step 1: Read & Extract Issues

#### Step 1a: Read file & detect document type

1. **Read the file from the provided path.** If the file contents are already in context (via an `@` reference), use what's there — but do NOT summarize, extract, or analyze ahead. Just proceed to type detection.
2. Detect the document type:
   - **Granola JSON** — top-level `id`, `title`, `notes_markdown`, `transcript[]` fields
   - **Granola Obsidian note** — YAML frontmatter with `granola_id`, `title`, `granola_url`, `tags`; body uses `###` headings + bullet points
   - **Markdown bug list** — `##` category headings, `###` individual bugs, prefixes like "Bug:", "UX:", "Task:"
   - **Raw transcript** — speaker labels, timestamps, conversational text
   - **General document** — fallback: structured lists, action-oriented language

#### Step 1b: Route by document type

```
Granola JSON with 200+ utterances    → Chunked pipeline (Steps 1c–1e)
Granola JSON with <200 utterances    → Single-pass transcript-first (Step 1f)
Raw Transcript with 300+ lines       → Chunked pipeline (Steps 1c–1e)
Raw Transcript with <300 lines       → Single-pass transcript-first (Step 1f)
Granola Obsidian / Markdown Bug List / General Doc → Single-pass structured (Step 1f)
```

**Routing confirmation (required):** After determining the route, output the routing decision to the user (see Pre-Flight Check above). Do not proceed to extraction until this output has been presented.

#### Step 1c: Chunk transcript into overlapping segments

**Timestamped transcripts (Granola JSON):**
- 5-minute windows with 2-minute overlaps
- Chunk 1: 0:00–5:00, Chunk 2: 3:00–8:00, Chunk 3: 6:00–11:00, etc.
- Utterances in the overlap zone appear in both adjacent chunks

**Non-timestamped transcripts (Raw Transcript):**
- 80-line chunks with 20-line overlaps
- If timestamps are parseable from text (e.g., `[00:12:34]`), prefer time-based chunking

Record metadata per chunk: start time, end time, overlap boundaries, utterance count, position in sequence.

#### Step 1d: Spawn chunk analysis agents

Read `references/chunk-agent-prompt.md` for the prompt template. Use the `Task` tool to spawn agents in batches of 3–4. Each agent receives:
- Its chunk of raw transcript text
- Chunk metadata (boundaries, overlap zones, position in sequence)
- The chunk agent prompt from the template
- All chunk time ranges (so agents can flag cross-chunk references)

Also calculate the video time offset for this batch: `video_time = utterance.start_timestamp - first_utterance.start_timestamp`, formatted as `H:MM:SS`. Pass this to agents so they can include video-referenceable timestamps.

```
Task tool config:
  subagent_type: "general-purpose"
  mode: "bypassPermissions"
```

#### Step 1e: Synthesis — merge chunk results

After all agents complete:

1. **Collect** all extracted issues from all chunks
2. **Overlap dedup** — for issues in the overlap zone between adjacent chunks, compare by timestamp proximity and topic. Merge duplicates, keeping the richer version (more detail, better quotes, higher confidence)
3. **Cross-chunk connections** — when agents flag references to other timeframes, search other chunks' results and link related issues (these may be a single issue with cause-effect separated across chunks)
4. **Notes cross-reference** (Granola JSON only) — compare transcript issues against `notes_markdown`:
   - Match found in both → enrich with notes language
   - Found only in notes → add with "notes-only" note
   - Found only in transcript → keep as-is (this is the key scenario that transcript-first catches)
5. Produce final extracted issue list for Step 2

#### Step 1f: Single-pass extraction

- **Structured documents** (Granola Obsidian, Markdown Bug List, General Doc): Unchanged — extract from document structure directly using patterns from `references/extraction-patterns.md`
- **Short transcripts** (Granola JSON <200 utterances, Raw Transcript <300 lines): Transcript-first ordering with the enhanced extraction approach (including Visual Gap Indicators from `references/extraction-patterns.md`), then cross-reference against notes for enrichment

For each extracted issue, capture:
   - **Title** — concise, action-oriented summary
   - **Description** — full context from the source
   - **Source quote** — exact text from the document, with video timestamp if available (e.g., `at 1:37:05 in recording`)
   - **Video timestamp** — `H:MM:SS` offset from recording start (for timestamped transcripts)
   - **Suggested priority** — based on signal words (see extraction-patterns.md)
   - **Category** — functional grouping (e.g., "Onboarding", "Payments", "Design")
   - **Type** — bug, task, or feature request (determines which description template to use — see `references/issue-template.md`)
   - **Visual flag** — `[Potential visual issue]` if identified through Visual Gap Indicators

### Step 2: Internal Dedup

Before building the working document, compare extracted issues against each other. Look for:
- Issues with overlapping titles (similar noun phrases, same subject)
- Issues where one is a subset of another (e.g., "Fix checkout timeout" vs. "Fix checkout timeout for large carts")
- Issues that describe the same problem from different angles

If overlapping pairs are found, present them to the user:
```
These extracted issues may overlap:

  A) "Fix checkout timeout on large carts"
  B) "Checkout fails when cart has 50+ items"

  These appear to describe the same underlying issue.

  Options:
  - Merge into one issue (pick which title to keep)
  - Keep both as separate issues
  - Remove one (pick which to remove)
```

Resolve all internal overlaps before proceeding.

### Step 3: Build Working Document

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

### Step 4: Gather Linear Configuration

Use `AskUserQuestion` to collect Linear settings. Fetch real data from Linear MCP to populate choices.

1. **Team** — call `mcp__claude_ai_Linear__list_teams` and present options
2. **Labels** — call `mcp__claude_ai_Linear__list_issue_labels` for the chosen team, then ask which labels to apply to all issues
3. **Project** — call `mcp__claude_ai_Linear__list_projects` for the chosen team and ask which project to assign issues to (or "None")
4. **Assignee** — ask if the user wants to assign issues to someone; if yes, call `mcp__claude_ai_Linear__list_users`
5. **Parent issue** — ask if issues should be sub-issues of a parent (user provides identifier or UUID)
6. **Status** — call `mcp__claude_ai_Linear__list_issue_statuses` for the chosen team if user wants a non-default status

Present defaults clearly. Allow the user to set per-issue overrides (e.g., different labels or parent for specific issues).

### Step 5: Linear Duplicate Search & Resolution

**Important — UUID tracking:** Linear's triage automation can move issues between teams after creation, which changes the human-readable identifier (e.g., WOOPRD-1234 becomes WOOPLUG-567). The UUID never changes. Always track created issues by their UUID, not their identifier.

#### Step 5a: Multi-Strategy Linear Search

For each confirmed issue, search for duplicates using multiple strategies. Run them in order and stop when plausible matches are found:

**Strategy 1 — Parent sub-issue check** (only when `parentId` is set):
```
list_issues({ parentId: "<parent-uuid>", limit: 50 })
```
Compare all existing sub-issues of the parent against the new issue title and description. This is the highest-confidence signal — if the parent already has a sub-issue covering the same topic, it's almost certainly a duplicate.

**Strategy 2 — Team + query search with 3 variants** (always runs if Strategy 1 found nothing):

Run up to 3 query variants, each with `limit: 30`:

**Variant 1 — Title noun phrases:**
```
list_issues({ team: "<team-key>", query: "<key noun phrases from title>", limit: 30 })
```
Extract meaningful noun phrases from the title — not just 2-3 random words. For example, for "Fix checkout timeout when processing large carts", search "checkout timeout large carts".

**Variant 2 — Description key terms:**
```
list_issues({ team: "<team-key>", query: "<synonyms/related terms from description>", limit: 30 })
```
Use synonyms or related terms from the description. For example, if the description mentions "payment processing hangs", search "payment processing hang".

**Variant 3 — User-visible symptom:**
```
list_issues({ team: "<team-key>", query: "<how a user would describe the problem>", limit: 30 })
```
Describe the problem from the user's perspective — how they'd report it. For example, "spinning loader checkout" or "can't complete purchase". This catches issues titled differently but describing the same observable behavior.

**Early-stop:** If any variant returns a HIGH confidence match (same behavior described, active issue), skip remaining variants for that issue.

Deduplicate results across all query variants before presenting.

**Strategy 3 — Cross-team search** (only if Strategies 1-2 found nothing):
```
list_issues({ query: "<key noun phrases>", limit: 20 })
```
Omit the `team` parameter to search across all teams. This catches issues that were filed under a different team or moved by triage automation.

#### Step 5b: Confidence Assessment

After collecting all candidates from the search strategies, assess each match and assign a confidence label:

- **HIGH** — same behavior described, same UI elements/flows, issue is active (Open, In Progress, Backlog)
- **MEDIUM** — related topic or overlapping description, but not clearly the same issue, or issue is in a different state
- **LOW** — tangentially related, already resolved (Done/Cancelled), or only superficial title similarity

Confidence is based on:
- **Title similarity** — do they describe the same problem?
- **Description overlap** — same UI elements, flows, error states?
- **Status relevance** — active issue (higher confidence) vs. Done/Cancelled (lower confidence)

Order candidates HIGH → MEDIUM → LOW when presenting.

#### Step 5c: Duplicate Presentation & Resolution

When potential duplicates are found, present them with full context and confidence labels:

```
Issue "Fix checkout timeout" may already exist:

  1. WOOPRD-1234: "Checkout times out on large carts"
     Team: WooProduct | Status: In Progress | Priority: High
     Assignee: Jane Smith | Updated: 3 days ago
     Match confidence: HIGH — same behavior, active issue

  2. WOOPLUG-567: "Payment timeout handling"
     Team: WooPlugins | Status: Done | Priority: Medium
     Assignee: — | Updated: 2 weeks ago
     Match confidence: LOW — related topic, already resolved

Options:
  a) Create anyway (no relation)
  b) Create and link as related to [pick which existing issue]
  c) Mark as duplicate — skip creation
  d) Skip entirely
```

For option (b), use the `relatedTo` parameter in `create_issue` to link the new issue to the existing one in a single call.

### Step 6: User Confirms Issues

Present the final list with all Linear configuration and duplicate resolution status applied:

```
## Ready to Import (N issues)

### 1. [Title]
- Team: [team name]
- Labels: [label1, label2, ...]
- Parent: [parent identifier] (if set)
- Assignee: [name] (if set)
- Duplicate status: No matches found / Linked to TEAM-XXXX / Create anyway
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

### Step 7: Import Issues

#### Step 7a: Batch Awareness

**For 10+ issues**, suggest using parallel agents grouped by category to speed up creation. When parallelizing:
- Group by category to minimize cross-agent overlap
- 2-3 agents per batch
- **Share the full list of all issue titles with each agent** so they can avoid creating issues that another agent in the batch is also creating. Each agent should check its assigned issues against the full title list and flag any cross-category overlaps before creating.
- Each agent runs the full multi-strategy search (5a) before creating
- Wait for each batch to complete before starting the next

#### Step 7b: Issue Creation

For issues that pass duplicate checking:

1. **Create the issue** using `mcp__claude_ai_Linear__create_issue`. **REQUIRED:** Each issue description MUST use the template from `references/issue-template.md` matching its Type (Bug Report, Action Item, or Feature Request). Include the source attribution block from Step 0c. Do not use freeform descriptions.
2. **After each `create_issue` call, store the UUID** (`id` field) from the response — not just the `identifier`. The UUID is the only stable reference once triage automation runs.
3. **Never re-search by identifier to verify creation.** If `create_issue` returned a UUID, the issue exists. Searching by the old identifier after triage routing has moved it will return nothing, which is not a failure — do not re-create the issue.

### Step 8: Generate Summary

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
- `references/chunk-agent-prompt.md` — prompt template for chunk analysis agents (used in Step 1d)