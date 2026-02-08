# CLAUDE.md — Project Instructions for Claude Code

## Repository Standards

This repo follows Scott Leimroth's standard repository format. All AI agents (Claude Code, Sid, Alex, sub-agents) must follow these rules.

## Required Files

Every repo MUST contain:
1. **README.md** — With a download/demo badge at the top (see badge rules below)
2. **CREDENTIALS.md** — API keys and secrets (ALWAYS .gitignored, NEVER committed)
3. **SECURITY_AUDIT.md** — Security checklist
4. **TODO.md** — Development log and task tracker
5. **.gitignore** — Must include CREDENTIALS.md, .env, .env.*, *.key, *.pem
6. **CLAUDE.md** — This file

If any of these files are missing, create them immediately before doing other work.

## README Badge Rules

The first thing after the title MUST be a prominent link to whatever the user can actually use:

- **Downloadable (APK/EXE):** `[![Download](https://img.shields.io/badge/DOWNLOAD-APK-green?style=for-the-badge)](RELEASE-URL)`
- **Web app/demo:** `[![Live Demo](https://img.shields.io/badge/LIVE-DEMO-blue?style=for-the-badge)](URL)`
- **Website:** `[![Visit Site](https://img.shields.io/badge/VISIT-SITE-blue?style=for-the-badge)](URL)`
- **Library/package:** `[![npm](https://img.shields.io/npm/v/PACKAGE?style=for-the-badge)](URL)`
- **Docs/research:** `[![Read Docs](https://img.shields.io/badge/READ-DOCS-orange?style=for-the-badge)](URL)`

**Rule: If someone visits the repo, they must immediately know how to try it.**

## TODO.md Format

```markdown
# PROJECT NAME - Development Log

## Last Session
- **Date:** YYYY-MM-DD
- **Summary:** What was worked on
- **Key changes:** What was added/fixed/modified
- **Stopped at:** Exactly where work left off
- **Blockers:** Anything preventing progress

## Current Status
### Working Features
### In Progress
### Known Bugs

## TODO - Priority
1. [ ] Task

## TODO - Nice to Have
- [ ] Enhancement

## Completed
- [x] Task (YYYY-MM-DD)

## Notes
```

## Workflow

1. **Start session** → Read TODO.md first to pick up where you left off
2. **During work** → Update TODO.md as features are built
3. **Before commit** → Run SECURITY_AUDIT.md checklist, confirm CREDENTIALS.md is NOT staged
4. **On release** → Ensure README badge links to latest release/demo
5. **End of session** → Update TODO.md "Last Session" section

## Code Style

- Clear, descriptive variable names
- Comments explaining WHY, not WHAT
- No hardcoded secrets — use environment variables
- Keep functions small and focused

## Repo Naming

- Sid's repos: `sid-` prefix
- Alex's repos: `alex-` prefix
- Scott's personal repos: no prefix

## Quality Bar

- README clear enough to understand in 30 seconds
- No broken links
- No placeholder text
- Download/demo links must work
- Concise — no walls of text
