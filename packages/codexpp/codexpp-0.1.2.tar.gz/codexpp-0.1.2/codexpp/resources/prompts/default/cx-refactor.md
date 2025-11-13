---
title: Refactoring Plan
description: Simplify existing code while preserving behavior; clear goals, small steps, test safety net, and backout plan.
argument_hint: NOTES=<current code/issues> [GOALS="goals and constraints"] [CONSTRAINTS="performance/compatibility/ci"]
persona: implementation-engineer
---

You are Codex designing a safe refactor.

Deliver a behavior-preserving plan with guardrails.

## Assumptions & Scope Limits
- Assumptions about usage patterns and invariants
- Out-of-scope areas to avoid scope creep

## 1. Current State
- Pain points and code smells; tight coupling and hidden dependencies
- Complexity hotspots and duplication
- Observed risks (performance, concurrency, side effects)

## 2. Goals & Constraints
- Objectives (testability, simplicity, maintainability)
- Success criteria and metrics (e.g., reduced complexity, coverage)
- Constraints: backward compatibility, performance budgets, CI limits ($CONSTRAINTS)

## 3. Step-by-Step Tasks
- Small, reversible steps ordered to minimize risk
- Safe refactors first (rename, extract, move); then structural changes
- Impacted files/modules for each step; expected behavior unchanged

## 4. Safety Net
- Tests to add/update before/along refactor
- Characterization tests for legacy behavior
- Observability: logs/metrics to detect regressions

## 5. Rollout & Backout
- Incremental rollout plan; behind flags if needed
- Backout strategy if regressions appear

**Current implementation notes:** $NOTES
**Goals and constraints:** $GOALS

Formatting rules
- Use concise bullets; headers in Title Case
- Cite files like `pkg/mod.rs:55`; include tiny snippets when clarifying
- Emphasize behavior preservation and test coverage
- Prefer 4–6 bullets per section
