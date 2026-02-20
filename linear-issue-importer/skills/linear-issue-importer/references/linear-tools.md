# Linear MCP Tool Reference

Quick reference for the Linear MCP tools used in the import workflow.

---

## List Teams

```
mcp__claude_ai_Linear__list_teams()
```

Returns all teams the user has access to. Each team has:
- `id` — UUID (used for API calls)
- `key` — short identifier (e.g., "WOOPRD")
- `name` — display name

Use in **Step 3** to let the user pick a team.

---

## List Issue Labels

```
mcp__claude_ai_Linear__list_issue_labels({ teamId: "<team-id>" })
```

Returns labels available for a team. Each label has:
- `id` — UUID
- `name` — display name (use this in `create_issue`)

Use in **Step 3** to present label options.

---

## List Issue Statuses

```
mcp__claude_ai_Linear__list_issue_statuses({ teamId: "<team-id>" })
```

Returns workflow states for a team (e.g., Backlog, Todo, In Progress, Done).

Use in **Step 3** if the user wants to set a specific status.

---

## List Projects

```
mcp__claude_ai_Linear__list_projects({ teamId: "<team-id>" })
```

Returns projects for a team. Each project has:
- `id` — UUID
- `name` — display name

Use in **Step 3** if the user wants to assign issues to a project.

---

## List Users

```
mcp__claude_ai_Linear__list_users()
```

Returns organization members. Each user has:
- `id` — UUID
- `name` — display name

Use in **Step 3** if the user wants to assign issues.

---

## List Issues (Search & Duplicate Check)

```
mcp__claude_ai_Linear__list_issues({
  team: "<team-key>",           // optional — omit to search all teams
  query: "<search terms>",      // searches title + description (fuzzy)
  parentId: "<parent-uuid>",    // optional — filter to sub-issues of a parent
  limit: 20                     // max 250, default varies
})
```

Search for existing issues. Used in **Step 5** for multi-layer duplicate checking.

**Parameters:**

| Param | Required | Description |
|-------|----------|-------------|
| `team` | No | Team key (e.g., "WOOPRD"). Omit to search across all teams. |
| `query` | No | Free-text search across title and description. Fuzzy matching — "checkout timeout" matches "Checkout times out on large carts". Searches all statuses (open and closed). |
| `parentId` | No | UUID of a parent issue. Returns only direct sub-issues of that parent. Highest-confidence signal for duplicate checking when importing sub-issues. |
| `limit` | No | Max results to return. Default varies by context; max is 250. Use 20 for query searches, 50 for parent sub-issue lookups. |

**Search strategies (used in Step 5):**

1. **Parent sub-issue check** — `list_issues({ parentId: "<uuid>", limit: 50 })` — when importing as sub-issues, always check existing children first. This is the highest-confidence duplicate signal.
2. **Team + query search** — `list_issues({ team: "<key>", query: "<noun phrases>", limit: 20 })` — primary search. Extract key noun phrases from the issue title, not just 2-3 random words.
3. **Cross-team search** — `list_issues({ query: "<key phrases>", limit: 10 })` — fallback when team-scoped search finds nothing. Omit `team` to search the entire workspace.

**Tips:**
- Use noun phrases from the title, not filler words (e.g., "checkout timeout handling" not "fix the timeout")
- Run a second query variant with synonyms/related terms from the description for better recall
- A match doesn't mean it's a duplicate — always present to user for decision

---

## Get Issue (by UUID)

```
mcp__claude_ai_Linear__get_issue({
  id: "<issue-uuid>",
  includeRelations: true          // optional — include related issues
})
```

Fetch a single issue by its UUID. Returns the issue's **current** state, including:
- `id` — UUID (stable, never changes)
- `identifier` — human-readable ID (e.g., "TEAM-1234") — **this can change** if triage automation moves the issue to a different team
- `url` — current URL (also changes if the issue moves teams)
- `title`, `description`, `state`, `assignee`, `labels`, `priority`, etc.

When `includeRelations: true` is set, the response also includes related issues (linked via `relatedTo`).

Use in **Step 6** to get the up-to-date identifier and URL for every created issue before building the summary. This is critical because triage routing can move issues between teams within minutes of creation.

**Why UUID, not identifier?** If you create an issue and get back `WOOPRD-1234`, triage automation might move it to `WOOPLUG-567` seconds later. Searching for `WOOPRD-1234` will return nothing. The UUID always works.

---

## Create Issue

```
mcp__claude_ai_Linear__create_issue({
  team: "<team-key>",
  title: "<issue title>",
  description: "<markdown description>",
  labels: ["Label1", "Label2"],
  parentId: "<parent-issue-uuid>",     // optional
  projectId: "<project-uuid>",         // optional
  assigneeId: "<user-uuid>",          // optional
  priority: 0-4,                       // optional: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
  stateId: "<status-uuid>",           // optional
  relatedTo: "<issue-uuid>"           // optional — link as related to an existing issue
})
```

Creates a new issue. Returns the created issue with:
- `id` — UUID
- `identifier` — human-readable ID (e.g., "TEAM-1234")
- `url` — link to the issue in Linear

**`relatedTo` parameter:** Links the newly created issue as "related to" the specified issue. Use this when the user chooses "Create and link as related" during duplicate checking — it creates the issue and establishes the relationship in a single call.

Use in **Step 5** after duplicate check passes.
