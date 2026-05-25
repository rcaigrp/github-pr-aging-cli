import unittest
import sys
import os
import datetime
import responses

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from github_pr_aging_cli import fetch_org_repos, fetch_repo_prs, calculate_days_open, filter_stale_prs, calculate_review_density, generate_report

class TestGithubPRAgingCLI(unittest.TestCase):
    def setUp(self):
        self.org = "testorg"
        self.token = "testtoken"
        self.repo = "testrepo"
        self.mock_prs = [
            {
                "created_at": "2023-01-01T00:00:00Z",
                "number": 1,
                "user": {"login": "testuser"},
                "base": {"repo": {"name": "testrepo"}},
                "html_url": "http://test.com/pr1"
            }
        ]

    @responses.activate
    def test_fetch_org_repos(self):
        responses.add(responses.GET, "https://api.github.com/orgs/testorg/repos", json=[{"name": "repo1"}, {"name": "repo2"}])
        responses.add(responses.GET, "https://api.github.com/orgs/testorg/repos", json=[])
        repos = fetch_org_repos(self.org, self.token)
        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]["name"], "repo1")

    @responses.activate
    def test_fetch_repo_prs(self):
        responses.add(responses.GET, "https://api.github.com/repos/testrepo/pulls", json=self.mock_prs)
        responses.add(responses.GET, "https://api.github.com/repos/testrepo/pulls", json=[])
        prs = fetch_repo_prs(self.repo, self.token)
        self.assertEqual(len(prs), 1)
        self.assertEqual(prs[0]["number"], 1)

    @unittest.mock.patch('github_pr_aging_cli.datetime')
    def test_calculate_days_open(self, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 2, 1, tzinfo=datetime.timezone.utc)
        days = calculate_days_open(self.mock_prs[0])
        self.assertEqual(days, 31)

    @unittest.mock.patch('github_pr_aging_cli.calculate_days_open')
    def test_filter_stale_prs(self, mock_days):
        mock_days.return_value = 20
        stale = filter_stale_prs(self.mock_prs, days=14)
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0]["number"], 1)

    @unittest.mock.patch('github_pr_aging_cli.datetime')
    @responses.activate
    def test_calculate_review_density(self, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 2, 1, tzinfo=datetime.timezone.utc)
        responses.add(responses.GET, "https://api.github.com/repos/testrepo/issues/1/comments", json=[{"body": "lgtm"}] * 5)
        density = calculate_review_density(self.mock_prs[0], self.token)
        self.assertAlmostEqual(density, 5 / 31, places=2)

    def test_generate_report(self):
        report = generate_report(self.mock_prs, self.token)
        self.assertIsInstance(report, str)
