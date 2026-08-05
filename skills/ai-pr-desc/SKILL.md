---
name: ai-pr-desc
description: >-
  AI-powered Pull Request description generator. Gathers git context (base branch, commits, diff stat, linked issues)
  and drafts a structured PR description. This skill should be used when the user asks to write a PR description,
  "生成PR说明", "写个pull request", "summarize my changes", or before opening/updating a pull request. Groups changes
  by Conventional Commits type and supports bilingual (中/英) output.
agent_created: true
---

# AI Pull Request Description Generator

Draft a clear, reviewer-friendly PR description from the actual git context — not from
memory. The skill runs a helper to collect commits, changed files, and linked issues, then
structures them into a standard PR template.

## When to Use

- User asks to "写个 PR 描述" / "generate a PR description" / "summarize my changes"
- Before opening a pull request
- When updating an existing PR's description
- After finishing a feature/fix branch and preparing to merge

## Workflow

### Step 1: Gather Context

Run the helper to collect grounded facts:

```bash
# Auto-detect base branch (main/master/develop), list commits & changed files
python3 scripts/gen_pr_context.py --json

# Or specify a base explicitly
python3 scripts/gen_pr_context.py --base main --json
```

The helper returns: current branch, detected base, commit list (`base..HEAD`),
`diff --stat` of changed files, linked issues parsed from commit messages
(`#123`, `Closes #456`), and a Conventional Commits type breakdown.

If the repo is outside the workspace, pass a path:
`python3 scripts/gen_pr_context.py /path/to/repo --base main`.

### Step 2: Confirm Audience & Sections

Ask (if not obvious) what to emphasize: bug fix, feature, refactor, or infra. Default
template:

```markdown
## Summary
<2-3 sentences: what and why>

## Changes
- <grouped by type: Features / Fixes / Refactor / ...>

## Test plan
- [ ] <how to verify>

## Screenshots / Notes
<if UI or config changes>

## Checklist
- [ ] Self-reviewed
- [ ] Tests added/updated
- [ ] Docs updated (if needed)
```

### Step 3: Draft the Description

Rules:
- **Lead with why**, then what. A reviewer should understand the intent in 10 seconds.
- **Group commits by type** using the Conventional Commits breakdown (feat → Features,
  fix → Fixes, refactor → Refactor, etc.). Collapse trivial/chore commits.
- **Reference issues** with `#123` so GitHub auto-links; mark `Closes #x` for fixes.
- Include a concrete **test plan** (commands the reviewer can run).
- Keep it scannable; avoid dumping the raw diff.
- Match the user's language (中文 / English).

### Step 4: Present

Show the drafted description and the detected base branch. Do NOT run `git push` or
open the PR unless the user explicitly asks. Offer to write it to a file (e.g.
`PR_DESCRIPTION.md`) if useful.

## Examples

### Feature PR
```markdown
## Summary
Adds a project scanner so README generation is grounded in the actual codebase
instead of a generic template.

## Changes
- Features: `scan_project.py` detects stack, languages, entry points
- Tests: unit tests for manifest parsing

## Test plan
- [ ] `python3 scripts/scan_project.py . --json`
- [ ] Verify output lists correct languages

Closes #42
```

## Anti-patterns to Avoid

- Describing changes you didn't verify against the git context
- A wall of raw diff with no narrative
- Missing the "why" and test plan
- Auto-pushing or opening the PR without being asked

## Reference

- `scripts/gen_pr_context.py`: git context collector (Python standard library only)
