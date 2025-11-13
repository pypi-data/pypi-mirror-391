"""CLI entry point for quber-workflow package."""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from .version import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """
    Quber Workflow - Shared Claude Code workflow for Quber projects.

    Provides Jira + GitHub automation, agents, skills, and templates.
    """
    pass


@main.command()
@click.option('--project', required=True, help='Project name (e.g., quber-analyst)')
@click.option('--package', required=True, help='Python package name (e.g., quber_analyst)')
@click.option('--repo', required=True, help='GitHub repo (e.g., xmandeng/quber-analyst)')
@click.option('--jira-key', default='QUE', help='Jira project key (default: QUE)')
def init(project: str, package: str, repo: str, jira_key: str):
    """Initialize quber workflow in current project."""
    console.print(Panel.fit(
        f"[bold green]Initializing Quber Workflow[/bold green]\n\n"
        f"Project: {project}\n"
        f"Package: {package}\n"
        f"Repo: {repo}\n"
        f"Jira Key: {jira_key}",
        border_style="green"
    ))

    from .commands.init import run_init
    run_init(project, package, repo, jira_key)


@main.command()
def update():
    """Update workflow files to latest version."""
    console.print("[bold yellow]Updating Quber Workflow...[/bold yellow]")
    from .commands.update import run_update
    run_update()


@main.command()
def migrate():
    """Migrate existing project to use Quber Workflow."""
    console.print("[bold blue]Migrating to Quber Workflow...[/bold blue]")
    from .commands.migrate import run_migrate
    run_migrate()


@main.command()
def clean():
    """Remove workflow-managed files from .git/info/exclude."""
    console.print("[bold cyan]Cleaning up git exclude entries...[/bold cyan]")
    from .git_utils import remove_from_git_exclude

    current_dir = Path.cwd()
    git_dir = current_dir / '.git'

    if not git_dir.exists():
        console.print("[bold red]✗ Not a git repository![/bold red]")
        console.print("This command only works in git repositories.")
        return

    exclude_file = git_dir / 'info' / 'exclude'
    if not exclude_file.exists():
        console.print("[yellow]No .git/info/exclude file found.[/yellow]")
        return

    # Show what will be removed
    from .git_utils import remove_from_git_exclude
    console.print("\nSearching for workflow-managed entries in .git/info/exclude...")

    # First, check what would be removed
    content = exclude_file.read_text()
    lines = content.splitlines()
    patterns_found = []
    in_quber_section = False

    for line in lines:
        if '# Files managed by quber-workflow' in line:
            in_quber_section = True
            continue
        if in_quber_section:
            if line.strip() and not line.strip().startswith('#'):
                patterns_found.append(line.strip())
            elif line.strip().startswith('#'):
                break

    if not patterns_found:
        console.print("[green]No workflow-managed entries found.[/green]")
        return

    console.print(f"\nFound {len(patterns_found)} workflow-managed entries:")
    for pattern in patterns_found:
        console.print(f"  • {pattern}")

    from rich.prompt import Confirm
    if Confirm.ask("\nRemove these entries?", default=True):
        removed = remove_from_git_exclude(None, current_dir)
        console.print(f"\n[bold green]✓ Removed {removed} entries from .git/info/exclude[/bold green]")
    else:
        console.print("[yellow]Cleanup cancelled[/yellow]")


if __name__ == '__main__':
    main()
