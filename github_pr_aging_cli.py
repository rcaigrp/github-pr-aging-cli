import requests
import datetime
import rich
from rich.console import Console
from rich.table import Table

class GitHubAPIError(Exception):
    pass

def fetch_org_repos(org: str, token: str) -> list[dict]:
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {"Authorization": f"token {token}"}
    repos = []
    page = 1
    while True:
        params = {"page": page, "per_page": 100}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise GitHubAPIError(f"Failed to fetch repos: {response.text}")
        data = response.json()
        repos.extend(data)
        if not data:
            break
        page += 1
    return repos

def fetch_repo_prs(repo: str, token: str) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"token {token}"}
    prs = []
    page = 1
    while True:
        params = {"page": page, "per_page": 100}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise GitHubAPIError(f"Failed to fetch PRs: {response.text}")
        data = response.json()
        prs.extend(data)
        if not data:
            break
        page += 1
    return prs

def calculate_days_open(pr: dict) -> int:
    created_at = datetime.datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
    return (datetime.datetime.now(datetime.timezone.utc) - created_at).days

def filter_stale_prs(prs: list[dict], days: int = 14) -> list[dict]:
    return [pr for pr in prs if calculate_days_open(pr) > days]

def calculate_review_density(pr: dict, token: str) -> float:
    repo_name = pr["base"]["repo"]["name"]
    pr_id = pr["number"]
    
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_id}/comments"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    comments = response.json()
    
    days_open = calculate_days_open(pr)
    if days_open == 0:
        return 0.0
    
    return len(comments) / days_open

def generate_report(prs: list[dict], token: str) -> str:
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("PR", style="dim")
    table.add_column("Author", style="green")
    table.add_column("Days Open", style="red")
    table.add_column("Review Density", style="blue")
    
    for pr in prs:
        days = calculate_days_open(pr)
        density = calculate_review_density(pr, token)
        table.add_row(
            f"#{pr['number']}",
            pr["user"]["login"],
            str(days),
            f"{density:.2f}"
        )
    
    console.print(table)
    return str(table)
