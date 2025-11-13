"""Git helper utilities for recommending commands."""

from pathlib import Path
from typing import Optional

from getupandrun.utils.logger import (
    print_info,
    print_prompt,
    print_section,
    print_success,
    print_warning,
)


class GitHelper:
    """Helper for generating Git command recommendations."""

    @staticmethod
    def is_git_repo(path: Path) -> bool:
        """
        Check if a directory is a Git repository.

        Args:
            path: Directory path to check

        Returns:
            True if .git exists
        """
        return (Path(path) / ".git").exists()

    @staticmethod
    def has_remote(path: Path) -> bool:
        """
        Check if Git repo has a remote configured.

        Args:
            path: Git repository path

        Returns:
            True if remote exists
        """
        if not GitHelper.is_git_repo(path):
            return False

        try:
            import subprocess

            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    @staticmethod
    def get_current_branch(path: Path) -> Optional[str]:
        """
        Get current Git branch name.

        Args:
            path: Git repository path

        Returns:
            Branch name or None
        """
        if not GitHelper.is_git_repo(path):
            return None

        try:
            import subprocess

            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            branch = result.stdout.strip()
            return branch if branch else None
        except Exception:
            return None

    @staticmethod
    def print_git_commands(project_path: Path, project_name: str) -> None:
        """
        Print recommended Git commands for a project.

        Args:
            project_path: Path to the project directory
            project_name: Name of the project
        """
        print_section("Git Commands")

        is_repo = GitHelper.is_git_repo(project_path)
        has_remote = GitHelper.has_remote(project_path) if is_repo else False
        current_branch = GitHelper.get_current_branch(project_path) if is_repo else None

        if not is_repo:
            # New repository - initialize and first commit
            print_info("Initialize a new Git repository:")
            print_prompt(f"  cd {project_name}")
            print_prompt("  git init")
            print_prompt("  git add .")
            print_prompt('  git commit -m "Initial commit: ' + project_name + '"')
            print_info("\nTo push to a remote repository:")
            print_prompt("  git remote add origin <your-repo-url>")
            print_prompt("  git branch -M main")
            print_prompt("  git push -u origin main")
        else:
            # Existing repository
            print_success("Git repository detected")
            if current_branch:
                print_info(f"Current branch: {current_branch}")

            print_info("\nAdd and commit your new project:")
            print_prompt(f"  cd {project_name}")
            print_prompt("  git add .")
            print_prompt('  git commit -m "Add ' + project_name + ' project"')

            if has_remote:
                print_info("\nPush to remote:")
                branch = current_branch or "main"
                print_prompt(f"  git push origin {branch}")
            else:
                print_warning("\nNo remote repository configured")
                print_info("To add a remote:")
                print_prompt("  git remote add origin <your-repo-url>")
                print_prompt("  git push -u origin main")

        # Additional helpful commands
        print_info("\nOther useful Git commands:")
        print_prompt("  git status          # Check repository status")
        print_prompt("  git log             # View commit history")
        print_prompt("  git diff            # View changes")
        print_prompt("  .gitignore          # Already created for you!")

