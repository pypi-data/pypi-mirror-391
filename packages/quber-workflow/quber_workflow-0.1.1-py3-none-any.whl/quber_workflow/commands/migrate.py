"""Migrate existing project to use quber workflow."""

import shutil
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..git_utils import add_to_git_exclude

console = Console()


def run_migrate():
    """
    Migrate an existing project to use quber workflow.

    This will:
    1. Backup existing .claude/ and .github/workflows/ (if they exist)
    2. Replace with quber-workflow templates
    3. Preserve settings.local.json (user-specific)
    4. Attempt to detect and preserve repo/project information
    """
    current_dir = Path.cwd()
    claude_dir = current_dir / '.claude'

    console.print("[bold yellow]⚠ Migration Warning[/bold yellow]")
    console.print("This will replace existing workflow files with quber-workflow templates.")
    console.print("Existing files will be backed up to [cyan].claude.backup/[/cyan]\n")

    if not Confirm.ask("Continue with migration?"):
        console.print("[yellow]Migration cancelled[/yellow]")
        return

    # Detect project information
    project_name = current_dir.name
    package_name = project_name.replace('-', '_')
    repo_name = f"your-org/{project_name}"

    # Try to detect from existing files
    if claude_dir.exists():
        skill_md = claude_dir / 'skills' / 'github-operations' / 'SKILL.md'
        if skill_md.exists():
            content = skill_md.read_text()
            for line in content.split('\n'):
                if 'Repository:' in line and '`' in line:
                    repo_name = line.split('`')[1]
                    break

    console.print(f"\n[dim]Detected settings:[/dim]")
    console.print(f"  Project: {project_name}")
    console.print(f"  Package: {package_name}")
    console.print(f"  Repo: {repo_name}\n")

    if not Confirm.ask("Are these settings correct?"):
        console.print("\n[yellow]Please run:[/yellow]")
        console.print(f"  [cyan]quber-workflow init \\[/cyan]")
        console.print(f"    [cyan]--project={project_name} \\[/cyan]")
        console.print(f"    [cyan]--package={package_name} \\[/cyan]")
        console.print(f"    [cyan]--repo={repo_name} \\[/cyan]")
        console.print(f"    [cyan]--jira-key=QUE[/cyan]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Migrating project...", total=None)

        # Backup existing files
        progress.update(task, description="Backing up existing files...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = current_dir / f'.claude.backup-{timestamp}'

        if claude_dir.exists():
            shutil.copytree(claude_dir, backup_dir / '.claude')

        gh_workflows = current_dir / '.github' / 'workflows'
        if gh_workflows.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(gh_workflows, backup_dir / '.github' / 'workflows')

        # Preserve settings.local.json
        settings_local = None
        if claude_dir.exists():
            settings_local_path = claude_dir / 'settings.local.json'
            if settings_local_path.exists():
                settings_local = settings_local_path.read_text()

        # Run initialization
        progress.update(task, description="Installing quber-workflow templates...")
        from .init import run_init
        run_init(project_name, package_name, repo_name, 'QUE')

        # Restore settings.local.json
        if settings_local:
            progress.update(task, description="Restoring user settings...")
            (claude_dir / 'settings.local.json').write_text(settings_local)

        progress.update(task, description="✓ Migration complete!", completed=True)

    console.print(f"\n[bold green]✓ Migration successful![/bold green]")
    console.print(f"\n[dim]Backup created at: {backup_dir}[/dim]")
    console.print("\nNext steps:")
    console.print("  1. Review changes in [cyan].claude/[/cyan]")
    console.print("  2. Verify environment variables are set")
    console.print("  3. Update any project-specific customizations")
