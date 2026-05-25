from rich.console import Console
from rich.table import Table

console = Console()

def generate_report(prs: List[Dict]):
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Repo", style="dim")
    table.add_column("PR #", style="bold cyan")
    table.add_column("Author", style="bold green")
    table.add_column("Days Open", style="bold yellow")
    table.add_column("Review Density", style="bold magenta")
    table.add_column("Link", style="blue underline")

    for pr in prs:
        days = pr.get('days_open', 0)
        if days < 7:
            color = "green"
        elif days <= 14:
            color = "yellow"
        else:
            color = "red"
        
        repo = pr.get('repo', 'N/A')
        pr_num = pr.get('number', 'N/A')
        author = pr.get('author', 'N/A')
        density = pr.get('review_density', 0.0)
        url = pr.get('url', '#')

        table.add_row(
            repo,
            str(pr_num),
            author,
            str(days),
            f"{density:.2f}",
            url
        )

    console.print(table)
