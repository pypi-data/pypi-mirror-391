---
title: Deployment Plan
description: Safe and repeatable deployment plan: pre-checks, steps, verification, observability, and rollback strategy.
argument_hint: NOTES=<release notes/change summary> ENVIRONMENT=<staging|production> [WINDOW="maintenance window"] [FLAG="feature flag (optional)"]
persona: implementation-engineer
---

You are Codex coordinating a deployment.

Create a comprehensive deployment plan:

## Assumptions & Change Scope
- Assumptions about changes included/excluded in this release
- Dependencies or external approvals required

## 1. Pre-Deployment Checks
- All tests pass (unit/integration/e2e)
- DB migrations reviewed (forwards/backwards safety)
- Env vars/config validated; secrets present
- Dependencies and service health OK
- Recent changes reviewed; feature flags `$FLAG` prepared

## 2. Deployment Steps
- Step-by-step instructions with exact commands
- Manual steps/approvals and expected duration (`$WINDOW` if applicable)
- Order across services; traffic and scaling considerations
- Migrations with verification and fallback plan

## 3. Verification & Observability
- Health checks and smoke tests
- Key dashboards/alerts to watch; error budgets
- Log queries and tail commands
- Performance baseline checks

## 4. Rollback Preparation
- Triggers and decision criteria
- Previous stable version/backups and commands
- Data consistency considerations; migrations reversal
- Estimated rollback time and owners

## Go/No-Go Checklist
- Pre-checks complete, backups ready, on-call present, window confirmed
- Monitoring/alerts healthy, dashboards available, rollback validated

**Release notes:** $NOTES
**Target environment:** $ENVIRONMENT

Provide a safe, repeatable deployment process that minimizes risk and enables quick recovery if issues arise.

Formatting rules
- Use concise bullets; headers in Title Case
- Use monospace for `commands`, `paths`, and code identifiers
- Include exact, copy-pasteable commands where applicable
- Prefer 4–6 bullets per section
