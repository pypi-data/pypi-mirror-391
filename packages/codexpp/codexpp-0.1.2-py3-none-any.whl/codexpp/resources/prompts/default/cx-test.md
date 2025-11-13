---
title: Testing Guidance
description: Practical test strategy for the change; key behaviors, coverage targets, and run commands.
argument_hint: CHANGE=<change summary> [TESTS="existing tests/notes"] [COVERAGE="% targets"]
persona: code-reviewer
---

You are Codex acting as a test strategist.

Develop a comprehensive testing strategy:

## Assumptions & Exit Criteria
- Assumptions about scope, risk level, and stability
- Exit criteria for adequate coverage and confidence

## 1. Key Behaviors to Validate
- Critical functionality and failure modes
- Edge cases, boundary conditions, and error paths
- Performance or scalability constraints
- Security-sensitive logic

## 2. Unit Test Recommendations
- Cases per function/method; happy-path and key branches
- Test data, fixtures, and mocks/stubs required
- Utilities/helpers to add for easier testing

## 3. Integration Test Plan
- Cross-component interactions and contracts
- End-to-end scenarios with setup/teardown
- External services/APIs to mock/fake

## 4. Test Updates Required
- Existing tests to update or delete; expected breakages
- Refactoring opportunities to reduce flakiness and duplication

## 5. Tooling & Commands
- Commands to run suites and focused tests
- Coverage tools and minimum targets ($COVERAGE)
- Debugging/profiling tools and tips
- CI/CD integration considerations

**Change summary:** $CHANGE
**Existing test suites:** $TESTS
**Coverage targets:** $COVERAGE

Provide actionable test recommendations that ensure code quality and prevent regressions.
