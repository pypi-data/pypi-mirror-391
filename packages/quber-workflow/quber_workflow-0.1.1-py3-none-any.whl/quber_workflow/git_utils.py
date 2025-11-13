"""Git utilities for managing local git ignore patterns."""

from pathlib import Path
from typing import List, Union, Optional


def add_to_git_exclude(files: Union[str, List[str]], repo_path: Path = None):
    """
    Add files to .git/info/exclude (local gitignore that never gets committed).

    Args:
        files: Single file path or list of file paths to add to exclude
        repo_path: Path to git repository (defaults to current directory)
    """
    if repo_path is None:
        repo_path = Path.cwd()

    # Ensure we're in a git repository
    git_dir = repo_path / '.git'
    if not git_dir.exists():
        # Not a git repo, silently skip
        return

    # Get the exclude file path
    exclude_file = git_dir / 'info' / 'exclude'

    # Ensure the info directory exists
    exclude_file.parent.mkdir(parents=True, exist_ok=True)

    # Normalize input to list
    if isinstance(files, str):
        files = [files]

    # Read existing patterns (if file exists)
    existing_patterns = set()
    if exclude_file.exists():
        existing_patterns = set(
            line.strip()
            for line in exclude_file.read_text().splitlines()
            if line.strip() and not line.strip().startswith('#')
        )

    # Add new patterns (skip duplicates)
    new_patterns = []
    for file_path in files:
        # Convert to relative path from repo root
        pattern = str(file_path)
        # Remove leading "./" if present, but keep leading "."
        if pattern.startswith('./'):
            pattern = pattern[2:]
        if pattern not in existing_patterns:
            new_patterns.append(pattern)
            existing_patterns.add(pattern)

    # If we have new patterns to add
    if new_patterns:
        # Check if we need to add header or newline before opening in append mode
        file_exists = exclude_file.exists()
        file_size = exclude_file.stat().st_size if file_exists else 0
        needs_newline = False
        needs_header = True

        if file_exists and file_size > 0:
            content = exclude_file.read_text()
            needs_newline = not content.endswith('\n')
            # Check if our header already exists
            if '# Files managed by quber-workflow' in content:
                needs_header = False

        with exclude_file.open('a') as f:
            # Add a comment header if we haven't added one before
            if needs_header:
                if file_exists and file_size > 0:
                    # Add a newline before our section if file has content
                    f.write('\n')
                f.write("# Files managed by quber-workflow\n")
            elif needs_newline:
                # Add newline if file doesn't end with one
                f.write('\n')

            # Add the patterns
            for pattern in new_patterns:
                f.write(f"{pattern}\n")


def remove_from_git_exclude(files: Optional[Union[str, List[str]]] = None, repo_path: Path = None) -> int:
    """
    Remove files from .git/info/exclude (local gitignore).

    Args:
        files: Single file path, list of file paths, or None to remove all quber-workflow entries
        repo_path: Path to git repository (defaults to current directory)

    Returns:
        Number of patterns removed
    """
    if repo_path is None:
        repo_path = Path.cwd()

    # Ensure we're in a git repository
    git_dir = repo_path / '.git'
    if not git_dir.exists():
        # Not a git repo, nothing to do
        return 0

    # Get the exclude file path
    exclude_file = git_dir / 'info' / 'exclude'
    if not exclude_file.exists():
        # No exclude file, nothing to do
        return 0

    # Read current content
    content = exclude_file.read_text()
    lines = content.splitlines()

    # Normalize files input to set
    patterns_to_remove = set()
    if files is None:
        # Remove all quber-workflow managed patterns
        # Find patterns between our comment marker and next comment or end
        in_quber_section = False
        for line in lines:
            if '# Files managed by quber-workflow' in line:
                in_quber_section = True
                continue
            if in_quber_section:
                if line.strip() and not line.strip().startswith('#'):
                    patterns_to_remove.add(line.strip())
                elif line.strip().startswith('#'):
                    # Hit another comment section, stop
                    break
    else:
        # Remove specific patterns
        if isinstance(files, str):
            files = [files]
        for file_path in files:
            pattern = str(file_path)
            # Remove leading "./" if present
            if pattern.startswith('./'):
                pattern = pattern[2:]
            patterns_to_remove.add(pattern)

    # Filter out the patterns to remove
    new_lines = []
    removed_count = 0
    skip_empty_after_header = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Keep the line if it's not a pattern we're removing
        if stripped in patterns_to_remove:
            removed_count += 1
            continue

        # If this is our header and all our patterns are being removed, skip the header too
        if '# Files managed by quber-workflow' in line:
            # Check if there are any quber-workflow patterns left after this line
            has_remaining_patterns = False
            for future_line in lines[i+1:]:
                if future_line.strip() and not future_line.strip().startswith('#'):
                    if future_line.strip() not in patterns_to_remove:
                        has_remaining_patterns = True
                        break
                elif future_line.strip().startswith('#'):
                    break

            if not has_remaining_patterns:
                skip_empty_after_header = True
                continue

        new_lines.append(line)

    # Write back the filtered content
    if removed_count > 0:
        # Remove trailing empty lines
        while new_lines and not new_lines[-1].strip():
            new_lines.pop()

        # Write back
        if new_lines:
            exclude_file.write_text('\n'.join(new_lines) + '\n')
        else:
            # If empty, write back the default template
            exclude_file.write_text(
                "# git ls-files --others --exclude-from=.git/info/exclude\n"
                "# Lines that start with '#' are comments.\n"
                "# For a project mostly in C, the following would be a good set of\n"
                "# exclude patterns (uncomment them if you want to use them):\n"
                "# *.[oa]\n"
                "# *~\n"
            )

    return removed_count
