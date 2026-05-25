import pytest
import responses
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/src")

from github_fetch import get_repos, get_prs, filter_stale, calculate_density, generate_report

class TestGithubFetch:
    @responses.activate
    def test_criterion_1_fetch_repos(self):
        org = "testorg"
        token = "testtoken"
        url = f"https://api.github.com/orgs/{org}/repos"
        responses.add(responses.GET, url, json=[{"name": "repo1"}, {"name": "repo2"}], status=200)
        responses.add(responses.GET, url, json=[], status=200)
        repos = get_repos(org, token)
        assert len(repos) == 2

    @responses.activate
    def test_criterion_1_fetch_prs(self):
        repo = "testorg/repo1"
        url = f"https://api.github.com/repos/{repo}/pulls"
        responses.add(responses.GET, url, json=[{"number": 1, "updated_at": "2023-01-01T00:00:00Z", "created_at": "2023-01-01T00:00:00Z", "user": {"login": "dev"}}], status=200)
        responses.add(responses.GET, url, json=[], status=200)
        prs = get_prs(repo, "token")
        assert len(prs) == 1

    def test_criterion_2_filter_stale(self):
        prs = [{"number": 1, "updated_at": "2023-01-01T00:00:00Z", "created_at": "2023-01-01T00:00:00Z", "user": {"login": "dev"}}]
        stale = filter_stale(prs, days=14)
        assert len(stale) == 1
        prs_new = [{"number": 2, "updated_at": "2025-01-01T00:00:00Z", "created_at": "2025-01-01T00:00:00Z", "user": {"login": "dev"}}]
        stale_all = filter_stale(prs + prs_new, days=14)
        assert len(stale_all) == 1

    def test_criterion_2_calculate_density(self):
        pr = {"updated_at": "2023-01-01T00:00:00Z", "created_at": "2023-01-01T00:00:00Z"}
        density = calculate_density(pr, 10)
        assert density == 10.0

    def test_criterion_3_generate_report(self):
        data = {"testorg/repo1": [{"number": 1, "updated_at": "2023-01-01T00:00:00Z", "created_at": "2023-01-01T00:00:00Z", "user": {"login": "dev"}}]}
        result = generate_report(data, "token")
        assert result is not None
