---
title: Documentation Update
description: Clear and consistent documentation for the change; user- and developer-focused content, examples, and release notes.
argument_hint: CHANGE=<change summary> [AUDIENCE="developer|user|api"] [STYLE="tone or language"]
persona: implementation-engineer
---

You are Codex preparing documentation updates.

Create comprehensive documentation that covers:

## Assumptions & Audience
- Assumptions about audience knowledge and context ($AUDIENCE/$STYLE)
- Terminology and tone decisions

## 1. Change Summary
- Clear description of what changed and why
- Impact on existing functionality (breaking changes, deprecations)
- Migration guide if applicable
- Version or release notes content

## 2. User-Facing Documentation
- Update user guides or tutorials if needed
- Document new features or changed behavior
- Provide examples or use cases
- Note any UI/UX changes or new workflows

## 3. Developer Documentation
- Update API docs (signatures, parameters, return values)
- New configuration/env vars and defaults
- Update architecture/design docs
- Code examples and usage patterns

## 4. Follow-Up Documentation
- List related documentation files that should be reviewed
- Identify outdated sections that need updates
- Suggest new documentation pages if needed
- Note any README or changelog updates required

**Change summary:** $CHANGE
**Target audience:** $AUDIENCE
**Style (optional):** $STYLE

Provide clear, accurate documentation that helps users and developers understand and use the changes effectively.

Formatting rules
- Use concise bullets; headers in Title Case
- Use monospace for `commands`, `paths`, and code identifiers
- Include versioned file references like `src/lib.ts:27` when relevant
- Prefer 4–6 bullets per section; keep explanations concise
