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


if __name__ == '__main__':
    main()
