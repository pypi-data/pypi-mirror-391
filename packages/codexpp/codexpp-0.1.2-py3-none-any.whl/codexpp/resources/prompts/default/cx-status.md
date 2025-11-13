---
title: Operational Status Briefing
description: Concise, action-oriented report on system health, SLI/SLO status, performance indicators, and risks.
argument_hint: SCOPE=<service/module> [METRICS="dashboard links/summary"] [SLO="targets"]
persona: system-architect
---

You are Codex compiling an operational status briefing.

Create a comprehensive status report:

## Assumptions
- Assumptions about time window, load patterns, and SLO applicability

## 1. Current Health Status
- Overall status (healthy/degraded/down) with rationale
- Availability/uptime and error budget usage (if SLOs exist)
- Recent deployments/changes and correlated effects
- Infra health (compute, DB, caches, network)

## 2. Key Performance Metrics
- Latency (p50/p95/p99) and trend
- Throughput and saturation indicators
- Error rates and dominant failure modes
- Resource utilization (CPU, memory, I/O, network)
- Business KPIs (if applicable)

## 3. Outstanding Incidents
- Active incidents and severity
- Resolution progress and ETA
- Known issues or workarounds
- Planned maintenance or changes

## 4. Risk Assessment
- Performance degradation and capacity headroom
- Security findings and exposure surface
- Technical debt and maintenance backlog
- External dependency risks

## 5. Recommended Actions
- Immediate actions to stabilize or improve
- Short-term optimizations and fixes
- Long-term strategic recommendations
- Monitoring/alerting enhancements and owners

**Service scope:** $SCOPE
**Latest metrics:** $METRICS
**SLO targets:** $SLO

Provide a clear, actionable status report that helps stakeholders understand system health and prioritize operational improvements.

Formatting rules
- Use concise bullets; headers in Title Case
- Include time windows for trends (e.g., last 24h/7d)
- Reference dashboards by name/url when available
- Conclude with 3–5 prioritized next actions
