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

## List Issues (Duplicate Check)

```
mcp__claude_ai_Linear__list_issues({
  team: "<team-key>",
  query: "<2-3 key terms>",
  limit: 5
})
```

Search for existing issues. Use in **Step 5** before creating each issue.

**Tips for effective duplicate searching:**
- Use 2-3 key terms from the issue title, not the full title
- Search is fuzzy — "checkout timeout" will match "Checkout times out on large carts"
- Check both open and closed issues (the search covers all statuses)
- A match doesn't mean it's a duplicate — present to user for decision

---

## Get Issue (by UUID)

```
mcp__claude_ai_Linear__get_issue({ id: "<issue-uuid>" })
```

Fetch a single issue by its UUID. Returns the issue's **current** state, including:
- `id` — UUID (stable, never changes)
- `identifier` — human-readable ID (e.g., "TEAM-1234") — **this can change** if triage automation moves the issue to a different team
- `url` — current URL (also changes if the issue moves teams)
- `title`, `description`, `state`, `assignee`, `labels`, etc.

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
  assigneeId: "<user-uuid>",           // optional
  priority: 0-4,                       // optional: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
  stateId: "<status-uuid>"             // optional
})
```

Creates a new issue. Returns the created issue with:
- `id` — UUID
- `identifier` — human-readable ID (e.g., "TEAM-1234")
- `url` — link to the issue in Linear

Use in **Step 5** after duplicate check passes.
