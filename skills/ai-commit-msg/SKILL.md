---
name: ai-commit-msg
description: >-
  AI-powered git commit message generator. Analyzes staged changes (git diff) and generates semantic,
  conventional commit-style messages. This skill should be used when the user asks to generate a commit message,
  write a commit, "帮我写commit", "生成commit信息", or after completing code changes and needing a message.
  Supports Conventional Commits, Angular, and custom formats.
agent_created: true
---

# AI Commit Message Generator

Generate high-quality, semantic git commit messages from staged diffs. Follows Conventional Commits
specification with intelligent scope detection.

## When to Use

- User asks to generate a commit message
- After making code changes that need committing
- "帮我写个commit" / "generate a commit message"
- Reviewing staged changes before commit

## Workflow

### Step 1: Get the Diff

Run one of these commands based on context:

```bash
git diff --staged          # Staged changes only (preferred)
git diff HEAD              # All changes since last commit
git diff --staged --stat   # Summary first, then full diff if needed
```

If the diff is very large (>500 lines), first show `--stat` summary, then focus on logical groups.

### Step 2: Analyze the Changes

Identify:
- **Type of change**: feat, fix, refactor, perf, docs, style, test, chore, ci, build
- **Scope**: Which module/component/package is affected
- **Breaking changes**: Any API or behavior changes that break compatibility
- **Multiple logical changes**: Should this be split into multiple commits?

If the diff contains multiple unrelated changes, suggest splitting into separate commits.

### Step 3: Generate the Message

Follow the Conventional Commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Type Rules

| Type | When to Use |
|------|-------------|
| `feat` | New feature or functionality |
| `fix` | Bug fix |
| `refactor` | Code restructuring without feature/fix |
| `perf` | Performance improvement |
| `docs` | Documentation only |
| `style` | Formatting, whitespace, semicolons (no code change) |
| `test` | Adding or updating tests |
| `chore` | Build process, dependencies, tooling |
| `ci` | CI/CD configuration changes |
| `build` | Changes affecting build system or external dependencies |
| `revert` | Reverting a previous commit |

#### Scope Detection

Auto-detect scope from changed file paths:
- `src/components/Button.tsx` → scope: `button`
- `pkg/auth/login.go` → scope: `auth`
- `api/users/routes.py` → scope: `users`

If a single module is changed, use it. If multiple, pick the most significant or omit scope.

#### Description Rules
- Use imperative mood: "add" not "added", "fix" not "fixed"
- Keep under 72 characters
- No period at end
- Describe WHAT and WHY, not HOW (the diff shows HOW)

#### Body (Optional)
Add body when the change needs more context:
- Explain motivation for the change
- Contrast with previous behavior
- Wrap at 72 characters

#### Footer (Optional)
- `BREAKING CHANGE: <description>` for breaking changes
- `Closes #123`, `Fixes #456` for issue references
- `Reviewed-by: @username`
- `Refs: #789`

### Step 4: Present and Confirm

Present the generated message and ask if the user wants to:
1. Use as-is
2. Edit before committing
3. Split into multiple commits
4. Regenerate with different parameters

Do NOT auto-commit. Always get confirmation first.

## Examples

### Simple fix
```
fix(login): resolve null pointer when session expires

The session timeout callback was not checking for null user object,
causing a crash when the session expired during an active request.
```

### Feature with breaking change
```
feat(api): migrate user endpoints to v2 authentication

BREAKING CHANGE: v1 auth tokens are no longer accepted.
Use the /auth/v2/token endpoint to obtain new tokens.

Closes #234
```

### Multi-file refactor
```
refactor(database): extract connection pool to shared module

Move connection pool management from individual services
to a shared db package. Reduces code duplication and
centralizes pool configuration.
```

### Performance
```
perf(search): add composite index for user search queries

Reduces search query time from ~800ms to ~50ms on the
users table with 1M+ records by adding a composite index
on (status, created_at, username).
```

## Language Support

The generated commit message should be in the same language the user is communicating in:
- English by default
- Chinese (中文) if the user is communicating in Chinese
- Follow the user's preference

## Anti-patterns to Avoid

- Generic messages like "fix bugs" or "update code"
- Messages that repeat the diff content
- Messages longer than 72 characters in the subject line
- Multiple unrelated changes in one commit
- Missing context about WHY the change was made
