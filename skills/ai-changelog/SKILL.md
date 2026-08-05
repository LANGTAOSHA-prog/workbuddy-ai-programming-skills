---
name: ai-changelog
description: >-
  AI-powered CHANGELOG generator. Parses git history (Conventional Commits) and produces a Keep a Changelog section
  grouped by type (Added/Fixed/Changed/...). This skill should be used when the user asks to generate a changelog,
  "生成更新日志", "写CHANGELOG", "release notes", or before cutting a release. Supports tagging from the latest git
  tag, explicit version ranges, and bilingual (中/英) section titles.
agent_created: true
---

# AI Changelog Generator

Produce release notes / CHANGELOG entries directly from git history. The skill parses
commits, strips Conventional Commits prefixes, groups them into standard sections, and
renders a Keep a Changelog–style markdown fragment you can paste into `CHANGELOG.md`.

## When to Use

- User asks to "生成更新日志" / "写 CHANGELOG" / "release notes" / "生成发布说明"
- Before tagging a release
- When `CHANGELOG.md` needs a new version section
- Summarizing what changed since the last tag

## Workflow

### Step 1: Generate the Section

Run the helper against the repo:

```bash
# Since the latest tag, labelled 1.2.0, dated today
python3 scripts/gen_changelog.py --version 1.2.0

# Explicit range and output to a file
python3 scripts/gen_changelog.py --range v1.0.0..v1.1.0 --version 1.1.0 --output section.md

# Dry-run as JSON to inspect grouping before writing
python3 scripts/gen_changelog.py --version Unreleased --json
```

Behavior:
- `--since TAG` / auto-detects the **latest git tag** as the start point (omitted → all history).
- Groups by Conventional Commits type:
  `feat→Added`, `fix→Fixed`, `perf→Performance`, `refactor/style→Changed`,
  `docs→Documentation`, `test→Tests`, `build/ci→Build`, `chore→Chore`,
  `revert→Reverted`, others → `Other`.
- Strips the `type(scope):` prefix and appends the short commit hash.
- If no commits match, emits `_No notable changes._`.

Run from outside the workspace with a path:
`python3 scripts/gen_changelog.py /path/to/repo --version 1.0.0`.

### Step 2: Review & Tidy

- Collapse trivial commits (e.g. multiple `chore` tweaks) into one line if noisy.
- Reorder sections to match your project's CHANGELOG convention (default order:
  Added → Changed → Fixed → Performance → Documentation → Tests → Build → Chore → Reverted → Other).
- For breaking changes (`feat!: ` or `!:`), add a **BREAKING CHANGES** note under Changed.

### Step 3: Write / Present

- Prepend the new section to the top of `CHANGELOG.md` under the `# Changelog` heading.
- Never overwrite existing entries; only insert above them.
- If the user only wants a draft, present the markdown and stop.

## Examples

### Generated fragment
```markdown
## [1.2.0] - 2026-08-05

### Added
- GitHub Actions CI workflow (`a1b2c3d4`)
- Dark mode toggle (`e5f6a7b8`)

### Fixed
- Null pointer on empty config (`c9d0e1f2`)

### Changed
- Refactored auth module into standalone package (`1a2b3c4d`)
```

## Anti-patterns to Avoid

- Hand-writing entries from memory instead of the git history
- Dropping commit hashes (they help reviewers trace changes)
- Mixing unrelated releases into one section
- Overwriting the existing CHANGELOG instead of prepending

## Reference

- `scripts/gen_changelog.py`: changelog generator (Python standard library only)
