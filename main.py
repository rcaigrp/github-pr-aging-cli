import requests
import rich
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any
import sys

def fetch_org_repos(org: str, token: str) -> List[Dict[str, Any]]:
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {"Authorization": f"token {token}"}
    repos = []
    page = 1
    while True:
        params = {"page": page, "per_page": 100}
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch repos: {resp.status_code}")
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def fetch_repos_prs(org: str, repos: List[Dict[str, Any]], token: str) -> List[Dict[str, Any]]:
    prs = []
    for repo in repos:
        url = f"https://api.github.com/repos/{org}/{repo['name']}/pulls"
        headers = {"Authorization": f"token {token}"}
        params = {"state": "open", "per_page": 100, "page": 1}
        while True:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code != 200:
                break
            data = resp.json()
            if not data:
                break
            prs.extend(data)
            params["page"] += 1
    return prs

def calculate_review_density(pr: Dict[str, Any]) -> float:
    date_str = pr['updated_at'].replace('Z', '+00:00')
    updated_at = datetime.fromisoformat(date_str)
    now = datetime.now(timezone.utc)
    days_open = (now - updated_at).days
    comments = pr.get('comments', 0)
    if days_open > 0:
        return comments / days_open
    return 0.0

def filter_stale_prs(prs: List[Dict[str, Any]], threshold: int = 14) -> List[Dict[str, Any]]:
    stale = []
    for pr in prs:
        date_str = pr['updated_at'].replace('Z', '+00:00')
        updated_at = datetime.fromisoformat(date_str)
        days_open = (datetime.now(timezone.utc) - updated_at).days
        if days_open > threshold:
            stale.append(pr)
    return stale

def generate_report(prs: List[Dict[str, Any]]):
    rich.print("[bold cyan]PR Aging Report[/bold cyan]")
    for pr in prs:
        date_str = pr['updated_at'].replace('Z', '+00:00')
        updated_at = datetime.fromisoformat(date_str)
        days_open = (datetime.now(timezone.utc) - updated_at).days
        density = calculate_review_density(pr)
        color = "red" if days_open > 30 else "yellow" if days_open > 14 else "green"
        repo_name = pr.get('base', {}).get('repo', {}).get('name', pr.get('repo', {}).get('name', 'Unknown'))
        rich.print(f"[{color}]{repo_name} #{pr['number']}[/{color}] Author: {pr['user']['login']}, Days: {days_open}, Density: {density:.2f}")

def main():
    parser = argparse.ArgumentParser(description="GitHub PR Aging CLI")
    parser.add_argument("--org", required=True, help="GitHub organization name")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    args = parser.parse_args()
    
    repos = fetch_org_repos(args.org, args.token)
    prs = fetch_repos_prs(args.org, repos, args.token)
    stale_prs = filter_stale_prs(prs)
    generate_report(stale_prs)

if __name__ == "__main__":
    main()
