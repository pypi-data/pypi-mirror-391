"""Initialize quber workflow in a project."""

import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from jinja2 import Template
from ..git_utils import add_to_git_exclude

console = Console()


def run_init(project: str, package: str, repo: str, jira_key: str):
    """
    Initialize quber workflow in the current project.

    Args:
        project: Project name (e.g., "quber-analyst")
        package: Python package name (e.g., "quber_analyst")
        repo: GitHub repository (e.g., "xmandeng/quber-analyst")
        jira_key: Jira project key (e.g., "QUE")
    """
    # Get template directory (inside installed package)
    template_dir = Path(__file__).parent.parent / 'templates'
    current_dir = Path.cwd()

    # Template variables
    context = {
        'project_name': project,
        'package_name': package,
        'repo_name': repo,
        'jira_project_key': jira_key,
    }

    # Track all files modified by this workflow
    modified_files = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Copy .claude/ directory
        task = progress.add_task("Creating .claude/ directory...", total=None)
        claude_dir = current_dir / '.claude'
        claude_dir.mkdir(exist_ok=True)

        # Copy agents
        progress.update(task, description="Copying agents...")
        agents_dir = claude_dir / 'agents'
        agents_dir.mkdir(exist_ok=True)
        for agent_file in (template_dir / 'agents').glob('*.md'):
            dest = agents_dir / agent_file.name
            shutil.copy2(agent_file, dest)
            modified_files.append(dest.relative_to(current_dir))

        # Copy skills
        progress.update(task, description="Copying skills...")
        skills_dir = claude_dir / 'skills'
        skills_dir.mkdir(exist_ok=True)

        # Copy jira-operations skill
        jira_skill_dir = skills_dir / 'jira-operations'
        shutil.copytree(
            template_dir / 'skills' / 'jira-operations',
            jira_skill_dir,
            dirs_exist_ok=True
        )
        # Track all files in the jira-operations directory
        for file in jira_skill_dir.rglob('*'):
            if file.is_file():
                modified_files.append(file.relative_to(current_dir))

        # Update jira-operations SKILL.md with repo name
        jira_skill_md = jira_skill_dir / 'SKILL.md'
        if jira_skill_md.exists():
            content = jira_skill_md.read_text()
            content = content.replace('{{REPO_NAME}}', repo)
            content = content.replace('xmandeng/quber_excel', repo)  # Replace hardcoded value
            jira_skill_md.write_text(content)

        # Copy github-operations skill
        gh_skill_dir = skills_dir / 'github-operations'
        shutil.copytree(
            template_dir / 'skills' / 'github-operations',
            gh_skill_dir,
            dirs_exist_ok=True
        )
        # Track all files in the github-operations directory
        for file in gh_skill_dir.rglob('*'):
            if file.is_file():
                modified_files.append(file.relative_to(current_dir))

        # Update github-operations SKILL.md with repo name
        gh_skill_md = gh_skill_dir / 'SKILL.md'
        if gh_skill_md.exists():
            content = gh_skill_md.read_text()
            content = content.replace('{{REPO_NAME}}', repo)
            content = content.replace('xmandeng/quber_excel', repo)  # Replace hardcoded value
            gh_skill_md.write_text(content)

        # Create settings.json (deny-based permissions)
        progress.update(task, description="Creating settings.json...")
        settings_json = claude_dir / 'settings.json'
        settings_content = '''{
  "permissions": {
    "allow": [
      "Bash(uv --version:*)",
      "Bash(tree:*)",
      "Bash(env)"
    ],
    "deny": [
      "Skill(jira-operations)",
      "Skill(github-operations)",
      "Bash(gh:*)",
      "Bash(curl:*atlassian:*)",
      "Bash(curl:*github.com/api:*)"
    ],
    "ask": []
  },
  "allowedMcpServers": []
}
'''
        settings_json.write_text(settings_content)
        modified_files.append(settings_json.relative_to(current_dir))

        # Copy GitHub workflows
        progress.update(task, description="Copying GitHub workflows...")
        gh_workflows_dir = current_dir / '.github' / 'workflows'
        gh_workflows_dir.mkdir(parents=True, exist_ok=True)
        jira_workflow = gh_workflows_dir / 'jira-transition.yml'
        shutil.copy2(
            template_dir / 'github-workflows' / 'jira-transition.yml',
            jira_workflow
        )
        modified_files.append(jira_workflow.relative_to(current_dir))

        # Copy documentation
        progress.update(task, description="Copying documentation...")
        docs_dir = current_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)

        for doc_file in (template_dir / 'docs').glob('*.md'):
            dest = docs_dir / doc_file.name
            shutil.copy2(doc_file, dest)
            modified_files.append(dest.relative_to(current_dir))

        # Add all modified files to .git/info/exclude
        progress.update(task, description="Adding files to local git ignore...")
        add_to_git_exclude([str(f) for f in modified_files], current_dir)

        progress.update(task, description="✓ Initialization complete!", completed=True)

    console.print("\n[bold green]✓ Quber workflow initialized successfully![/bold green]\n")
    console.print("Next steps:")
    console.print("  1. Review [cyan].claude/settings.json[/cyan] for permissions")
    console.print("  2. Set required environment variables:")
    console.print("     - GH_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN")
    console.print("     - ATLASSIAN_SITE_NAME")
    console.print("     - ATLASSIAN_USER_EMAIL")
    console.print("     - ATLASSIAN_API_TOKEN")
    console.print("  3. Configure GitHub secrets for Actions:")
    console.print("     - JIRA_BASE_URL")
    console.print("     - JIRA_USER_EMAIL")
    console.print("     - JIRA_API_TOKEN")
    console.print(f"\n[dim]Project configured: {project} ({repo})[/dim]")
