# Github-PR-Aging-CLI

## Goal
Build a Python CLI tool to track PR age, review activity, and tech debt across a GitHub organization.

## Status
**Active** (Resumed)

## Acceptance Criteria
1. Fetch all repos and PRs for a specified GitHub org using requests and GitHub REST API v3. Handle pagination and rate limits.
2. Filter PRs stale > 14 days (based on updated_at). Calculate review density = (PR comments + issue comments) / days_open.
3. Generate a formatted terminal report using rich. Columns: Repo, PR #, Author, Days Open, Review Density, Link. Color-code by age.

## Sprint Progress
- Meeting 4/8 completed.
- Resumed with +3 meetings budget.
- Focus: Robust pagination, mocking, and test coverage.
- Implemented github_pr_aging_cli.py and acceptance_tests.py.

## Known Issues
- Previous runs timed out due to pagination loops.
- Rich output interfered with test collection.

## Next Steps
- Run acceptance tests to validate implementation.
- Address any edge cases or failure modes.