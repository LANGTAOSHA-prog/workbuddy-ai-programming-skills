---
name: ai-code-review
description: >-
  AI-powered code review and analysis. This skill should be used when the user asks to review code, audit for bugs,
  check security vulnerabilities, analyze performance issues, or evaluate code quality and best practices. Supports
  JavaScript, TypeScript, Python, Go, Java, Rust, C/C++, and more. Triggers include: "review this code", "code review",
  "audit for bugs", "security check", "代码审查", "检查代码", "审查代码".
agent_created: true
---

# AI Code Review

Intelligent code review that goes beyond linting -- finds logic bugs, security vulnerabilities, performance
bottlenecks, and architecture issues across multiple languages.

## When to Use

Trigger this skill whenever the user asks to:

- Review or audit code for quality
- Find bugs, logic errors, or edge cases
- Check for security vulnerabilities (OWASP Top 10, injection, XSS, etc.)
- Analyze performance bottlenecks
- Evaluate adherence to best practices and design patterns
- Review pull requests or diffs

## Workflow

### Step 1: Understand Scope

Clarify what to review:
- A specific file or set of files
- A git diff or pull request
- Code snippets pasted directly
- An entire project or module

Ask the user for focus areas if not specified: security, performance, correctness, style, or all.

### Step 2: Analyze the Code

Read the target code thoroughly. For each file, perform these analyses:

#### Bug Detection
- Logic errors: off-by-one, inverted conditions, missing null checks
- Race conditions in concurrent code
- Resource leaks (unclosed files, connections, memory)
- Incorrect error handling or swallowed exceptions
- Type mismatches and implicit coercion risks
- Edge cases: empty inputs, boundary values, overflow

#### Security Audit
Check against OWASP Top 10:
- **Injection**: SQL, command, LDAP -- any unsanitized input passed to interpreters
- **XSS**: Unescaped user input in HTML/JS output
- **Authentication**: Weak password handling, missing MFA, session issues
- **Authorization**: Missing access controls, IDOR risks
- **Sensitive Data**: Hardcoded secrets, logging PII, insecure storage
- **SSRF**: User-controlled URLs in server-side requests
- **Deserialization**: Unsafe deserialization of user data
- **CSRF**: Missing tokens on state-changing requests
- **Dependencies**: Known vulnerabilities in third-party packages
- **Configuration**: Debug mode in production, exposed admin endpoints

#### Performance Analysis
- N+1 queries and inefficient database access patterns
- Unnecessary allocations or deep copies
- Blocking operations in async contexts
- Missing caching opportunities
- Algorithmic complexity issues (O(n^2) where O(n log n) is possible)
- Large payloads or unbounded collections

#### Code Quality
- SOLID principles adherence
- DRY violations and code duplication
- Naming clarity and consistency
- Function/method length and complexity
- Test coverage gaps
- Documentation completeness

### Step 3: Generate Report

Output a structured review report with these sections:

```
## Code Review Report

### Summary
Brief overall assessment (2-3 sentences).

### Critical Issues (must fix)
| # | File:Line | Issue | Severity | Suggestion |
|---|-----------|-------|----------|------------|

### Warnings (should fix)
| # | File:Line | Issue | Category | Suggestion |
|---|-----------|-------|----------|------------|

### Suggestions (nice to have)
| # | File:Line | Issue | Category | Suggestion |
|---|-----------|-------|----------|------------|

### Security Findings
Detailed per-finding with CWE reference where applicable.

### Performance Notes
Specific bottlenecks with before/after estimates.

### Positive Highlights
Things done well -- acknowledge good patterns.
```

### Step 4: Offer Fixes

After presenting the report, offer to generate fix patches for any issue.
When the user accepts, apply changes with the Edit tool, explaining each change.

## Language-Specific Checks

### JavaScript / TypeScript
- `==` vs `===`, `typeof` edge cases, `this` binding issues
- Promise anti-patterns (unhandled rejections, missing awaits)
- `any` type abuse in TypeScript
- React: missing keys, state mutation, useEffect dependencies

### Python
- Mutable default arguments, late-binding closures
- `except:` without specific exception type
- `is` vs `==` confusion
- `asyncio` misuse: blocking calls in coroutines

### Go
- Unchecked errors, goroutine leaks, defer in loops
- Nil interface vs nil pointer confusion
- Race conditions with shared maps

### Java
- NullPointerException risks, resource management (try-with-resources)
- Thread safety of collections, `equals`/`hashCode` contract
- Stream API misuse: side effects in `peek`

## Severity Levels

| Level | Meaning |
|-------|---------|
| **Critical** | Security vulnerability, data loss, crash in production |
| **High** | Logic bug that produces incorrect results |
| **Medium** | Performance issue, maintainability problem |
| **Low** | Style inconsistency, minor improvement |
