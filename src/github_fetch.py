import requests
from datetime import datetime
from rich.table import Table

def get_repos(org, token):
    url = f"https://api.github.com/orgs/{org}/repos"
    repos = []
    page = 1
    headers = {"Authorization": f"token {token}", "User-Agent": "github-pr-aging-cli"}
    while True:
        params = {"per_page": 100, "page": page}
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 403 or not resp.json():
            break
        repos.extend(resp.json())
        page += 1
    return repos

def get_prs(repo, token):
    url = f"https://api.github.com/repos/{repo}/pulls"
    prs = []
    page = 1
    headers = {"Authorization": f"token {token}", "User-Agent": "github-pr-aging-cli"}
    while True:
        params = {"per_page": 100, "page": page}
        resp = requests.get(url, headers=headers, params=params)
        if not resp.json():
            break
        prs.extend(resp.json())
        page += 1
    return prs

def filter_stale(prs, days=14):
    result = []
    now = datetime.now()
    for pr in prs:
        updated = datetime.strptime(pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        if (now - updated).days > days:
            result.append(pr)
    return result

def calculate_density(pr, comments):
    updated = datetime.strptime(pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
    created = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    days_open = max(1, (updated - created).days)
    return (comments or 0) / days_open

def generate_report(data, token):
    table = Table()
    table.add_column("Repo")
    table.add_column("PR #")
    table.add_column("Author")
    table.add_column("Days Open")
    table.add_column("Density")
    table.add_column("Link")
    for repo, prs in data.items():
        for pr in prs:
            updated = datetime.strptime(pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
            days_open = max(1, (datetime.now() - updated).days)
            density = calculate_density(pr, 0)
            table.add_row(repo, str(pr["number"]), pr["user"]["login"], str(days_open), f"{density:.2f}", f"https://github.com/{repo}/pulls/{pr['number']}")
    return table
