# Github-PR-Aging-CLI

## Goal
Build a Python CLI tool to track PR age, review activity, and tech debt across a GitHub organization.

## Status
Active (Budget: 8 meetings)

## Acceptance Criteria
1. Fetch all repos and PRs for a specified GitHub org using requests and GitHub REST API v3. Handle pagination and rate limits.
2. Filter PRs stale > 14 days (based on updated_at). Calculate review density = (PR comments + issue comments) / days_open.
3. Generate a formatted terminal report using rich. Columns: Repo, PR #, Author, Days Open, Review Density, Link. Color-code by age.

## Completed Work
- Implemented `src/github_fetch.py` with pagination, rate-limit handling, stale filtering, and density calculation.
- Created `acceptance_tests.py` mocking GitHub API via `responses`.
- All tests pass locally.

## Next Steps
- Integrate CLI entry point using `argparse`.
- Add configuration file support.
- Run acceptance tests in CI.
