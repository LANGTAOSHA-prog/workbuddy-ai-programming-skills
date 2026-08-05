---
name: ai-readme-gen
description: >-
  AI-powered README generator. Scans a project (directory tree, languages, manifest files, entry points) and drafts a
  clean, structured README.md. This skill should be used when the user asks to generate a README, write project
  documentation, "写个README", "生成项目说明", "create a readme", or when a repository lacks documentation. Supports
  multiple project types (Node/Python/Go/Rust/Java) and bilingual (中/英) output.
agent_created: true
---

# AI README Generator

Turn a bare or under-documented project into a clean, structured README.md. The skill first
runs a scanner to gather facts about the codebase, then drafts documentation that reflects
what the project actually is — not a generic template.

## When to Use

- User asks to "写个 README" / "generate a README" / "create project docs"
- A repository has no README or a stale/placeholder one
- After scaffolding a new project and needing first documentation
- Onboarding a project and wanting a quick overview doc

## Workflow

### Step 1: Scan the Project

Run the companion scanner to gather grounded facts (do not guess the stack):

```bash
# Human-readable summary
python3 scripts/scan_project.py . --depth 3

# Or full JSON for the model to consume
python3 scripts/scan_project.py . --depth 3 --json
```

The scanner detects:
- Directory tree (auto-skips `.git`, `node_modules`, `__pycache__`, build dirs)
- Languages by file extension count
- Manifest files and key metadata:
  - `package.json` → name, version, description, dependencies
  - `pyproject.toml` / `requirements.txt` → name, version, deps
  - `go.mod` → module path, Go version, deps
  - `Cargo.toml` → name, version
- Likely entry points (`main.py`, `index.js`, `main.go`, …)
- Whether a README already exists, and an estimated code-line count

If the project lives outside the workspace, you may pass an absolute path:
`python3 scripts/scan_project.py /path/to/project --depth 3`.

### Step 2: Confirm Scope

Ask the user (if not obvious) what sections they want. Default structure:

1. **Title + one-line description** (badge row optional)
2. **Features** — what the project does, in bullets
3. **Tech stack** — derived from the scan
4. **Installation** — commands specific to the detected manifest
5. **Usage / Quick start** — a minimal runnable example
6. **Project structure** — the scanned tree (trimmed)
7. **Configuration** — env vars / config files if any
8. **API / CLI reference** — only if the project exposes one
9. **Testing** — how to run tests
10. **Contributing / License** — link to existing files

### Step 3: Draft the README

Write in the same language as the user's request (中文 by default for Chinese users,
English otherwise). Rules:

- **Be accurate**: only claim what the scan or code supports. If unsure about a feature,
  read the relevant source file before asserting it.
- **Installation must match the stack**: `npm install` for Node, `pip install -e .` /
  `poetry install` for Python, `go build ./...` for Go, `cargo build` for Rust.
- **Usage examples must be real**: prefer commands that actually work for the detected
  entry point.
- Keep it scannable: short paragraphs, bullets, fenced code blocks with language tags.
- Avoid hype and filler. No "powerful", "robust", "blazing fast" without evidence.

### Step 4: Present and Write

Show the drafted README. On confirmation, write it to `README.md` at the project root
(overwrite only if the user agreed; never silently clobber an existing README — offer to
write `README.generated.md` instead).

## Examples

### Detected Node project
```markdown
## Installation
\`\`\`bash
npm install
\`\`\`

## Usage
\`\`\`bash
npm start
\`\`\`
```

### Detected Python project
```markdown
## Installation
\`\`\`bash
pip install -e .
\`\`\`

## Usage
\`\`\`bash
python -m my_package
\`\`\`
```

## Anti-patterns to Avoid

- Inventing dependencies or commands the scanner didn't find
- Copy-pasting a generic template with no relation to the codebase
- Over-long READMEs for tiny projects
- Claiming features without reading the source to confirm

## Reference

- `scripts/scan_project.py`: project scanner (Python standard library only)
