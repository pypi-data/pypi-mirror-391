---
title: Rollback Strategy
description: Rapid and safe rollback plan for critical issues; triggers, steps, communications, and post-incident root cause analysis.
argument_hint: INCIDENT=<issue summary/link> [VERSION="live version"] [DB_IMPACT="yes|no"] [FEATURE_FLAG="name (optional)"]
persona: implementation-engineer
---

You are Codex preparing an emergency rollback plan.

Create a comprehensive rollback strategy:

## Assumptions & Data Safety
- Assumptions about data mutations, backups, and migration reversibility
- SLAs and user impact tolerance during rollback

## 1. Incident Detection Signals
- Error rates, latency spikes, or service degradation indicators
- User reports or support tickets
- Monitoring alerts or dashboard anomalies
- Database or infrastructure issues
- Critical functionality failures

## 2. Rollback Decision Criteria
- Severity assessment (data loss, security breach, service outage)
- Impact scope (users affected, revenue impact, SLA violations)
- Time to resolution estimate
- Rollback vs. hotfix decision factors

## 3. Rollback Steps
- Immediate containment (disable `$FEATURE_FLAG`, throttle, route traffic)
- Step-by-step rollback to `$VERSION` with exact commands
- Database considerations: migrations reversible? `$DB_IMPACT` data fix needed?
- Service restarts/config reversion; cache invalidation as required

## 4. Communication Plan
- Stakeholder notification (team, management, users)
- Status update channels and frequency
- Incident timeline documentation
- User-facing communication templates
- Post-rollback status updates

## 5. Post-Incident Follow-Up
- Root cause analysis plan with owners and timeline
- Incident report, evidence, and action items
- Prevention measures and permanent fixes
- Monitoring/alerting improvements; dashboards and runbooks updates
- Team retrospective and lessons learned

**Incident summary:** $INCIDENT
**Current version:** $VERSION

Provide a clear, actionable rollback plan that enables rapid recovery while maintaining system integrity and user trust.

Formatting rules
- Use concise bullets; headers in Title Case
- Use monospace for `commands`, `paths`, and code identifiers
- Provide exact, copy-pasteable commands and owners where possible
- Prefer 4–6 bullets per section
