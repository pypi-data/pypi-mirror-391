---
title: Feature Implementation
description: Implement the feature in small, verifiable steps; minimal focused diffs, tests, and clear validation.
argument_hint: SPEC=<feature description> [NOTES="constraints or notes"] [FLAG="feature flag name (optional)"]
persona: implementation-engineer
---

You are Codex implementing a change in this repository.

Proceed in small, reviewable increments. If ambiguity blocks progress, ask up to 2 brief questions; otherwise state assumptions and continue.

## Assumptions & Questions
- Key assumptions about constraints and scope
- Up to 2 blocking questions if needed

## 1. Restate & Acceptance Criteria
- Restate goal and explicit acceptance criteria
- Call out constraints and rollout plan (use `$FLAG` if applicable)

## 2. Implementation Plan
- Sequence of small steps (commit-sized), each with:
  - Files to change/create and rationale
  - Data/control flow impact
  - Tests to add/update

## 3. Apply Changes
- Follow repo style; keep diffs minimal and focused
- Add error handling and edge case coverage
- Maintain backward compatibility or guard with `$FLAG`

## 4. Tests & Verification
- Unit/integration tests for each step
- Manual verification steps and commands
- Edge cases explicitly validated

## 5. Summary
- Modified/created files list with brief purpose
- Breaking changes or migrations (if any)
- How to test and verify success

**Feature request:** $SPEC
**Constraints or notes:** $NOTES

Formatting rules
- Use concise bullets; headers in Title Case
- Cite files like `src/module.py:88`; include small snippets if useful
- Be explicit about verification steps and commands
- Prefer 4–6 bullets per section
