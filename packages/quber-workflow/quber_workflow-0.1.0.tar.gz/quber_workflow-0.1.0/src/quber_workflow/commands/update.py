"""Update quber workflow files to latest version."""

import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

console = Console()


def run_update():
    """
    Update workflow files to the latest version from the package.

    This will update:
    - .claude/agents/
    - .claude/skills/
    - .github/workflows/jira-transition.yml
    - docs/ (workflow specs)

    User's .claude/settings.local.json is preserved.
    """
    template_dir = Path(__file__).parent.parent / 'templates'
    current_dir = Path.cwd()

    # Check if .claude/ exists
    claude_dir = current_dir / '.claude'
    if not claude_dir.exists():
        console.print("[bold red]✗ No .claude/ directory found![/bold red]")
        console.print("Run [cyan]quber-workflow init[/cyan] first to initialize the project.")
        return

    # Confirm update
    if not Confirm.ask("This will update workflow files. Continue?"):
        console.print("[yellow]Update cancelled[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Updating workflow files...", total=None)

        # Update agents
        progress.update(task, description="Updating agents...")
        agents_dir = claude_dir / 'agents'
        for agent_file in (template_dir / 'agents').glob('*.md'):
            shutil.copy2(agent_file, agents_dir)

        # Update skills
        progress.update(task, description="Updating skills...")
        skills_dir = claude_dir / 'skills'

        # Update jira-operations
        jira_skill_dir = skills_dir / 'jira-operations'
        if jira_skill_dir.exists():
            # Preserve any local modifications by reading old SKILL.md for repo name
            old_skill_md = jira_skill_dir / 'SKILL.md'
            repo_name = "your-org/your-repo"  # default
            if old_skill_md.exists():
                content = old_skill_md.read_text()
                # Extract repo name from existing SKILL.md
                for line in content.split('\n'):
                    if 'Repository:' in line:
                        repo_name = line.split('`')[1] if '`' in line else repo_name
                        break

            # Copy new version
            shutil.copytree(
                template_dir / 'skills' / 'jira-operations',
                jira_skill_dir,
                dirs_exist_ok=True
            )

            # Update with preserved repo name
            new_skill_md = jira_skill_dir / 'SKILL.md'
            if new_skill_md.exists():
                content = new_skill_md.read_text()
                content = content.replace('xmandeng/quber_excel', repo_name)
                new_skill_md.write_text(content)

        # Update github-operations
        gh_skill_dir = skills_dir / 'github-operations'
        if gh_skill_dir.exists():
            # Preserve repo name
            old_skill_md = gh_skill_dir / 'SKILL.md'
            repo_name = "your-org/your-repo"
            if old_skill_md.exists():
                content = old_skill_md.read_text()
                for line in content.split('\n'):
                    if 'Repository:' in line:
                        repo_name = line.split('`')[1] if '`' in line else repo_name
                        break

            shutil.copytree(
                template_dir / 'skills' / 'github-operations',
                gh_skill_dir,
                dirs_exist_ok=True
            )

            new_skill_md = gh_skill_dir / 'SKILL.md'
            if new_skill_md.exists():
                content = new_skill_md.read_text()
                content = content.replace('xmandeng/quber_excel', repo_name)
                new_skill_md.write_text(content)

        # Update GitHub workflow
        progress.update(task, description="Updating GitHub workflows...")
        gh_workflows_dir = current_dir / '.github' / 'workflows'
        gh_workflows_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            template_dir / 'github-workflows' / 'jira-transition.yml',
            gh_workflows_dir / 'jira-transition.yml'
        )

        # Update documentation
        progress.update(task, description="Updating documentation...")
        docs_dir = current_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)

        for doc_file in (template_dir / 'docs').glob('*.md'):
            shutil.copy2(doc_file, docs_dir)

        progress.update(task, description="✓ Update complete!", completed=True)

    console.print("\n[bold green]✓ Workflow files updated successfully![/bold green]")
    console.print("\n[dim]Note: .claude/settings.local.json was preserved (if it exists)[/dim]")
