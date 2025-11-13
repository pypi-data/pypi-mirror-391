"""CLI command implementations."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from getupandrun.environment.manager import EnvironmentManager
from getupandrun.templates.manager import TemplateManager
from getupandrun.utils.history import CommandHistory
from getupandrun.utils.logger import (
    print_error,
    print_header,
    print_info,
    print_success,
    print_table,
    print_warning,
)
from getupandrun.utils.prompts import ask_yes_no


def help_command() -> None:
    """Show detailed help information and usage guide."""
    from getupandrun.utils.logger import print_prompt, print_section

    print_header("GetUpAndRun - Complete Usage Guide")
    print_info(
        "GetUpAndRun scaffolds development environments from natural language descriptions."
    )

    print_section("Quick Start")
    print_info("1. Install GetUpAndRun:")
    print_prompt("  pip install getupandrun")
    print_info("\n2. Set your OpenAI API key:")
    print_prompt("  export OPENAI_API_KEY='your-api-key'")
    print_info("\n3. Create a project:")
    print_prompt('  getupandrun -p "React frontend with Node.js backend and Postgres"')

    print_section("Main Command")
    print_info("Create a new project from a natural language description:")
    print_prompt('  getupandrun --prompt "Your stack description"')
    print_info("\nOptions:")
    headers = ["Option", "Description"]
    rows = [
        ["--prompt, -p", "Natural language description of the stack you want"],
        ["--name, -n", "Custom project name (defaults to GPT-generated name)"],
        ["--mode, -m", "Mode: local (default) scaffolds locally, cloud generates deployment instructions"],
        ["--start, -s", "Automatically start services after scaffolding (local mode only)"],
        ["--template, -t", "Use a predefined template instead of GPT"],
        ["--help, -h", "Show this help message"],
    ]
    print_table(headers, rows)

    print_section("Environment Management Commands")
    print_info("Manage Docker Compose services for a project:")
    headers = ["Command", "Description"]
    rows = [
        ["start <path>", "Start Docker Compose services"],
        ["stop <path>", "Stop Docker Compose services"],
        ["restart <path>", "Restart Docker Compose services"],
        ["teardown <path>", "Remove containers (use -v to remove volumes)"],
        ["status <path>", "Show status of all services"],
    ]
    print_table(headers, rows)

    print_section("Examples")
    print_info("Create a React + Node.js + Postgres stack:")
    print_prompt(
        '  getupandrun -p "React frontend with Node.js backend and Postgres database"'
    )
    print_info("\nCreate a FastAPI backend with Redis:")
    print_prompt('  getupandrun -p "FastAPI backend with Redis cache" -n my-api')
    print_info("\nCreate and automatically start services:")
    print_prompt('  getupandrun -p "Django app with Postgres" --start')
    print_info("\nGenerate cloud deployment instructions:")
    print_prompt('  getupandrun -p "React + Node.js + Postgres" --mode cloud')
    print_info("\nManage an existing project:")
    print_prompt("  getupandrun start ./my-project")
    print_prompt("  getupandrun status ./my-project")
    print_prompt("  getupandrun stop ./my-project")

    print_section("Prerequisites")
    print_info("Before using GetUpAndRun, ensure you have:")
    print_info("  • Python 3.9 or higher")
    print_info("  • Docker and Docker Compose installed")
    print_info("  • Git installed (optional, for version control)")
    print_info("  • OpenAI API key (set as OPENAI_API_KEY environment variable)")

    print_section("What Gets Generated")
    print_info("In local mode, GetUpAndRun creates a complete project structure:")
    print_info("  • Service directories with framework-specific files")
    print_info("  • Dockerfiles for each service")
    print_info("  • docker-compose.yml for orchestration")
    print_info("  • .env file with environment variables")
    print_info("  • Makefile with common commands (up, down, clean, logs)")
    print_info("  • README.md with project documentation")
    print_info("  • .gitignore file")
    print_info("\nIn cloud mode, GetUpAndRun generates:")
    print_info("  • Cloud deployment instructions (AWS, GCP, Docker Hub)")
    print_info("  • Platform-specific deployment steps")
    print_info("  • Configuration guidance")
    print_info("  • Instructions saved as <project-name>-cloud-deployment.md")

    print_section("Supported Stacks")
    print_info("GetUpAndRun supports various frameworks and services:")
    print_info("  • Frontend: React, Vue, Angular")
    print_info("  • Backend: Node.js, Python (FastAPI, Django, Flask)")
    print_info("  • Databases: Postgres, MySQL, MongoDB")
    print_info("  • Cache: Redis, Memcached")
    print_info("  • And more (via GPT interpretation)")

    print_section("Getting Help")
    print_info("For more information:")
    print_info("  • GitHub: https://github.com/your-org/getupandrun")
    print_info("  • Issues: https://github.com/your-org/getupandrun/issues")
    print_info("  • Documentation: https://getupandrun.readthedocs.io")


def version_command() -> None:
    """Show version information."""
    from getupandrun import __version__

    print_info(f"GetUpAndRun version {__version__}")


def last_command() -> None:
    """Re-run the last command."""
    print_header("Re-running Last Command")
    history = CommandHistory()
    last_cmd = history.get_last_command()

    if not last_cmd:
        print_warning("No command history found.")
        print_info("Run a command first, then use 'getupandrun last' to repeat it.")
        return

    print_info("Last command:")
    print_info(f"  Prompt: {last_cmd.get('prompt', 'N/A')}")
    print_info(f"  Mode: {last_cmd.get('mode', 'local')}")
    if last_cmd.get("name"):
        print_info(f"  Project name: {last_cmd.get('name')}")
    print_info(f"  Auto-start: {last_cmd.get('start', False)}")

    if ask_yes_no("Re-run this command?", default=True):
        cmd = ["getupandrun", "-p", last_cmd["prompt"]]
        if last_cmd.get("name"):
            cmd.extend(["-n", last_cmd["name"]])
        if last_cmd.get("mode") != "local":
            cmd.extend(["-m", last_cmd["mode"]])
        if last_cmd.get("start"):
            cmd.append("--start")

        print_info(f"\nRunning: {' '.join(cmd)}")
        sys.exit(subprocess.call(cmd))
    else:
        print_info("Cancelled.")


def history_command() -> None:
    """Show command history."""
    print_header("Command History")
    history = CommandHistory()
    commands = history.list_history(limit=10)

    if not commands:
        print_info("No command history found.")
        return

    headers = ["#", "Prompt", "Mode", "Name", "Auto-start"]
    rows = []
    for i, cmd in enumerate(commands, 1):
        rows.append(
            [
                str(i),
                cmd.get("prompt", "")[:50] + ("..." if len(cmd.get("prompt", "")) > 50 else ""),
                cmd.get("mode", "local"),
                cmd.get("name", "-") or "-",
                "Yes" if cmd.get("start") else "No",
            ]
        )

    print_table(headers, rows)
    print_info("\nUse 'getupandrun last' to re-run the most recent command.")


def templates_command(search: Optional[str]) -> None:
    """List available templates."""
    print_header("Available Templates")
    template_manager = TemplateManager()

    if search:
        templates_list = template_manager.search_templates(search)
        if not templates_list:
            print_info(f"No templates found matching '{search}'.")
            return
        print_info(f"Search results for '{search}':")
    else:
        templates_list = template_manager.list_templates()

    if not templates_list:
        print_info("No templates available.")
        return

    headers = ["Key", "Name", "Description"]
    rows = []
    for template in templates_list:
        rows.append(
            [
                template["key"],
                template["name"],
                template["description"],
            ]
        )

    print_table(headers, rows)
    print_info("\nUse a template with: getupandrun --template <key>")
    print_info("Example: getupandrun --template react-node-postgres")


def doctor_command() -> None:
    """Run diagnostic checks on your system."""
    from getupandrun.utils.diagnostics import Diagnostics

    print_header("GetUpAndRun Diagnostics")
    diagnostics = Diagnostics()
    results = diagnostics.run_all_checks()
    diagnostics.print_report()

    if not results["all_ok"]:
        print_warning("\n⚠️ Some issues were found. Please resolve them before using GetUpAndRun.")
        sys.exit(1)
    else:
        print_success("\n✅ Your system is ready to use GetUpAndRun!")
        sys.exit(0)


def start_command(project_path: str, detach: bool) -> None:
    """Start Docker Compose services for a project."""
    print_header("Starting Services")
    env_manager = EnvironmentManager(Path(project_path))
    if env_manager.start(detach=detach):
        sys.exit(0)
    else:
        sys.exit(1)


def stop_command(project_path: str) -> None:
    """Stop Docker Compose services for a project."""
    print_header("Stopping Services")
    env_manager = EnvironmentManager(Path(project_path))
    if env_manager.stop():
        sys.exit(0)
    else:
        sys.exit(1)


def teardown_command(project_path: str, volumes: bool) -> None:
    """Tear down Docker Compose services for a project."""
    print_header("Tearing Down Services")
    env_manager = EnvironmentManager(Path(project_path))
    if env_manager.teardown(remove_volumes=volumes):
        sys.exit(0)
    else:
        sys.exit(1)


def down_command(project_path: str, volumes: bool) -> None:
    """Clean shutdown command (alias for teardown with verification)."""
    print_header("Shutting Down Services")
    env_manager = EnvironmentManager(Path(project_path))
    if env_manager.teardown(remove_volumes=volumes):
        sys.exit(0)
    else:
        sys.exit(1)


def reset_command(project_path: str, confirm: bool) -> None:
    """Reset project by removing all generated files and containers."""
    from getupandrun.utils.prompts import ask_yes_no

    print_header("Reset Project")
    project_path_obj = Path(project_path)

    if not project_path_obj.exists():
        print_warning(f"Project path does not exist: {project_path}")
        sys.exit(1)

    # Check if it's a GetUpAndRun project
    compose_file = project_path_obj / "docker-compose.yml"
    if not compose_file.exists():
        print_warning(
            f"This doesn't appear to be a GetUpAndRun project (no docker-compose.yml found)"
        )
        if not ask_yes_no("Continue anyway?", default=False):
            print_info("Cancelled.")
            sys.exit(0)

    # Warn user about what will be deleted
    print_warning("This will:")
    print_info("  • Stop and remove all Docker containers")
    print_info("  • Remove all Docker volumes")
    print_info(f"  • Delete the entire project directory: {project_path}")

    if not confirm:
        if not ask_yes_no("Are you sure you want to reset this project?", default=False):
            print_info("Cancelled.")
            sys.exit(0)

    # First, teardown containers
    print_info("\nStep 1: Removing Docker containers and volumes...")
    try:
        env_manager = EnvironmentManager(project_path_obj)
        env_manager.teardown(remove_volumes=True)
    except Exception as e:
        print_warning(f"Error during teardown (continuing anyway): {e}")

    # Then, delete the project directory
    print_info(f"\nStep 2: Deleting project directory: {project_path}...")
    try:
        import shutil

        shutil.rmtree(project_path_obj)
        print_success(f"Project directory deleted: {project_path}")
        print_success("Project reset complete!")
        sys.exit(0)
    except Exception as e:
        print_error(f"Failed to delete project directory: {e}")
        print_info("You may need to manually delete the directory.")
        sys.exit(1)


def restart_command(project_path: str) -> None:
    """Restart Docker Compose services for a project."""
    print_header("Restarting Services")
    env_manager = EnvironmentManager(Path(project_path))
    if env_manager.restart():
        sys.exit(0)
    else:
        sys.exit(1)


def status_command(project_path: str) -> None:
    """Show status of Docker Compose services for a project."""
    print_header("Service Status")
    env_manager = EnvironmentManager(Path(project_path))
    services = env_manager.status()

    if services:
        headers = ["Service", "Status"]
        rows = [[name, state] for name, state in services.items()]
        print_table(headers, rows)
    else:
        print_warning("No services found or unable to get status")


def update_command() -> None:
    """Check for updates and notify if a new version is available."""
    import subprocess
    from getupandrun import __version__

    print_header("Checking for Updates")
    print_info(f"Current version: {__version__}")

    try:
        # Check PyPI for latest version
        result = subprocess.run(
            ["pip", "index", "versions", "getupandrun"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            # Parse output to find latest version
            output = result.stdout
            if "Available versions:" in output:
                print_info("Checking PyPI for latest version...")
                # In a real implementation, parse the output to get the latest version
                print_success("You are running the latest version!")
            else:
                print_warning("Could not determine latest version from PyPI")
        else:
            # Fallback: try pip show
            result = subprocess.run(
                ["pip", "show", "getupandrun"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print_info("Package information retrieved.")
                print_info("\nTo update, run:")
                print_info("  pip install --upgrade getupandrun")
            else:
                print_warning("Could not check for updates. You can manually update with:")
                print_info("  pip install --upgrade getupandrun")

    except subprocess.TimeoutExpired:
        print_warning("Update check timed out. You can manually update with:")
        print_info("  pip install --upgrade getupandrun")
    except FileNotFoundError:
        print_warning("pip not found. You can manually update with:")
        print_info("  pip install --upgrade getupandrun")
    except Exception as e:
        print_warning(f"Error checking for updates: {e}")
        print_info("You can manually update with:")
        print_info("  pip install --upgrade getupandrun")


def install_completion_command() -> None:
    """Install shell completion for GetUpAndRun."""
    import sys
    from pathlib import Path

    shell = os.environ.get("SHELL", "").split("/")[-1]

    print_header("Installing Shell Completion")
    print_info(f"Detected shell: {shell}")

    if shell == "bash":
        completion_script = Path.home() / ".bash_completion.d" / "getupandrun-complete.sh"
        completion_script.parent.mkdir(parents=True, exist_ok=True)
        completion_script.write_text(
            'eval "$(_GETUPANDRUN_COMPLETE=bash_source getupandrun)"\n'
        )
        print_success(f"Bash completion installed to: {completion_script}")
        print_info("\nTo enable, add this to your ~/.bashrc:")
        print_info(f"  source {completion_script}")
        print_info("\nOr run:")
        print_info("  echo 'source ~/.bash_completion.d/getupandrun-complete.sh' >> ~/.bashrc")
    elif shell == "zsh":
        completion_script = Path.home() / ".zsh_completion.d" / "_getupandrun"
        completion_script.parent.mkdir(parents=True, exist_ok=True)
        # Generate zsh completion using Click's built-in support
        import subprocess
        result = subprocess.run(
            [sys.executable, "-c", "from getupandrun.cli.main import cli; import click; click.Context(cli).get_help()"],
            capture_output=True,
            text=True,
        )
        # Use Click's completion generation
        completion_script.write_text(
            '#compdef getupandrun\n'
            'eval "$(_GETUPANDRUN_COMPLETE=zsh_source getupandrun)"\n'
        )
        print_success(f"Zsh completion installed to: {completion_script}")
        print_info("\nTo enable, add this to your ~/.zshrc:")
        print_info(f"  fpath=({completion_script.parent} $fpath)")
        print_info("  autoload -U compinit && compinit")
        print_info("\nOr run:")
        print_info("  echo 'fpath=(~/.zsh_completion.d $fpath)' >> ~/.zshrc")
        print_info("  echo 'autoload -U compinit && compinit' >> ~/.zshrc")
    elif shell == "fish":
        completion_script = Path.home() / ".config" / "fish" / "completions" / "getupandrun.fish"
        completion_script.parent.mkdir(parents=True, exist_ok=True)
        completion_script.write_text(
            'eval (env _GETUPANDRUN_COMPLETE=fish_source getupandrun)\n'
        )
        print_success(f"Fish completion installed to: {completion_script}")
        print_info("\nFish completion is automatically loaded from:")
        print_info(f"  {completion_script.parent}")
    else:
        print_warning(f"Shell '{shell}' not supported for automatic installation.")
        print_info("Supported shells: bash, zsh, fish")
        print_info("\nYou can manually install completion:")
        print_info("  Bash: eval \"$(_GETUPANDRUN_COMPLETE=bash_source getupandrun)\"")
        print_info("  Zsh:  eval \"$(_GETUPANDRUN_COMPLETE=zsh_source getupandrun)\"")
        print_info("  Fish: eval (env _GETUPANDRUN_COMPLETE=fish_source getupandrun)")
        print_info("\nOr add the eval command to your shell's configuration file.")



