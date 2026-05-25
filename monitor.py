import os
import requests
from datetime import datetime
from typing import List, Dict

BASE_URL = "https://api.github.com"

def fetch_org_repos(org: str, token: str) -> List[str]:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    repos = []
    url = f"{BASE_URL}/orgs/{org}/repos"
    while url:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403:
            print(f"Rate limited for org {org}. Remaining: {resp.headers.get('X-RateLimit-Remaining')}")
            break
        if resp.status_code not in (200, 404):
            print(f"Error fetching repos for {org}: {resp.status_code}")
            break
        data = resp.json()
        repos.extend([r['full_name'] for r in data if 'full_name' in r])
        if 'next' in resp.headers.get('Link', ''):
            url = resp.headers['Link'].split(';')[0].replace('<', '').replace('>', '')
        else:
            url = None
    return repos

def fetch_prs(repo: str, token: str) -> List[Dict]:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    prs = []
    url = f"{BASE_URL}/repos/{repo}/pulls"
    while url:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 403 or resp.status_code == 404:
            print(f"Error fetching PRs for {repo}: {resp.status_code}")
            break
        if resp.status_code != 200:
            break
        data = resp.json()
        prs.extend(data)
        if 'next' in resp.headers.get('Link', ''):
            url = resp.headers['Link'].split(';')[0].replace('<', '').replace('>', '')
        else:
            url = None
    return prs

def calculate_review_density(pr: Dict, token: str) -> float:
    comments = 0
    comments += pr.get('comments', 0)
    issue_url = pr.get('issue_url')
    if issue_url:
        resp = requests.get(issue_url, headers={"Authorization": f"Bearer {token}"})
        if resp.status_code == 200:
            comments += resp.json().get('comments', 0)
    days_open = pr.get('days_open', 0)
    return comments / days_open if days_open > 0 else 0.0

def filter_stale_prs(prs: List[Dict], min_days: int) -> List[Dict]:
    return [pr for pr in prs if pr.get('days_open', 0) >= min_days]

def get_pr_age(pr: Dict) -> int:
    updated_at = pr.get('updated_at')
    if not updated_at:
        return 0
    dt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
    return (datetime.utcnow() - dt).days
