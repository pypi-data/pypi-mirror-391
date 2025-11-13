"""Main CLI entry point for GetUpAndRun."""

import sys
from typing import Optional

import click

from getupandrun.cloud.instructions import CloudInstructionGenerator
from getupandrun.cloud.detector import CloudDetector
from getupandrun.environment.manager import EnvironmentManager
from getupandrun.gpt.integration import GPTClient
from getupandrun.scaffold.engine import ScaffoldingEngine
from getupandrun.utils.git_helper import GitHelper
from getupandrun.templates.manager import TemplateManager
from getupandrun.utils.history import CommandHistory
from getupandrun.utils.logger import (
    create_progress_bar,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
    print_table,
)
from getupandrun.cli.bulk_commands import stop_all_command
from getupandrun.cli.commands import (
    down_command,
    doctor_command,
    help_command,
    history_command,
    last_command,
    reset_command,
    restart_command,
    start_command,
    status_command,
    stop_command,
    templates_command,
    teardown_command,
    version_command,
)
from getupandrun.utils.crash_logger import CrashLogger
from getupandrun.utils.errors import ErrorCode, GetUpAndRunError, handle_error
from getupandrun.utils.prompts import (
    ask_choice,
    ask_question,
    ask_yes_no,
    confirm_if_uncertain,
)
from getupandrun.utils.completion import get_mode_completions, get_template_completions


@click.group(invoke_without_command=True)
@click.option(
    "--prompt",
    "-p",
    type=str,
    help="Natural language description of the stack you want to create",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["local", "cloud"], case_sensitive=False),
    default="local",
    help="Mode selection: local (default) scaffolds locally, cloud generates deployment instructions",
    shell_complete=lambda ctx, param, incomplete: get_mode_completions(ctx, param, incomplete),
)
@click.option(
    "--name",
    "-n",
    type=str,
    default=None,
    help="Custom project name (defaults to GPT-generated name)",
)
@click.option(
    "--start",
    "-s",
    is_flag=True,
    default=False,
    help="Automatically start services after scaffolding",
)
@click.option(
    "--template",
    "-t",
    type=str,
    default=None,
    help="Use a predefined template (e.g., react-node-postgres)",
    shell_complete=lambda ctx, param, incomplete: get_template_completions(ctx, param, incomplete),
)
@click.pass_context
def cli(
    ctx: click.Context,
    prompt: Optional[str],
    mode: str,
    name: Optional[str],
    start: bool,
    template: Optional[str],
) -> None:
    """
    GetUpAndRun - Scaffold development environments from natural language.

    Describe your desired stack in plain English and GetUpAndRun will
    scaffold, install, and run it locally using Docker Compose.
    """
    # If no command is provided and no prompt, show help or interactive mode
    if ctx.invoked_subcommand is None:
        if prompt is None and template is None:
            # Interactive mode - ask for template or prompt
            print_header("GetUpAndRun - Interactive Mode")

            use_template = ask_yes_no(
                "Would you like to use a predefined template?", default=False
            )

            if use_template:
                # Show templates and let user choose
                template_manager = TemplateManager()
                templates = template_manager.list_templates()

                if not templates:
                    print_warning("No templates available.")
                    use_template = False
                else:
                    template_names = [t["name"] for t in templates]
                    selected_name = ask_choice(
                        "Select a template", template_names, default=template_names[0]
                    )
                    # Find the key for the selected template
                    template = next(
                        t["key"] for t in templates if t["name"] == selected_name
                    )
                    print_info(f"Selected template: {selected_name}")

            if not use_template:
                prompt = ask_question(
                    "Describe your desired stack",
                    validator=lambda x: len(x.strip()) > 0,
                )

            # Ask for optional parameters
            if ask_yes_no("Do you want to customize project settings?", default=False):
                name = ask_question("Project name (optional)", default=None, type=str)
                if name and not name.strip():
                    name = None

                mode_choice = ask_question(
                    "Mode",
                    default="local",
                    type=click.Choice(["local", "cloud"], case_sensitive=False),
                )
                mode = mode_choice

                start = ask_yes_no("Start services automatically after scaffolding?", default=False)
            else:
                name = None
                start = False

        # Main command logic
        print_header("GetUpAndRun")
        crash_logger = CrashLogger()
        try:
            # Save command to history
            history = CommandHistory()
            history.save_command(prompt or f"template:{template}", mode, name, start)

            # Get stack configuration from template or GPT
            if template:
                print_info(f"Using template: {template}")
                template_manager = TemplateManager()
                stack_config = template_manager.get_template(template)
                print_success(f"Template loaded: {stack_config.name}")
            else:
                # Initialize GPT client
                gpt_client = GPTClient()
                print_info(f"Mode: {mode}")

                # Interpret the prompt with progress indicator
                with create_progress_bar() as progress:
                    task = progress.add_task(
                        "[cyan]Interpreting your prompt with GPT...", total=None
                    )
                    stack_config = gpt_client.interpret_prompt(prompt)
                    progress.update(task, completed=True)

                # Display the generated configuration
                print_success("Stack configuration generated successfully!")

            # Display configuration (for both template and GPT)
            print_info(f"Project: {stack_config.name}")
            print_info(f"Description: {stack_config.description}")
            print_info(f"Services: {len(stack_config.services)}")

            # Only confirm if GPT-generated (not templates) and mismatches detected
            if not template and prompt:
                stack_config, final_prompt = confirm_if_uncertain(
                    prompt, stack_config, gpt_client
                )
                # Update prompt in history if it changed
                if final_prompt != prompt:
                    history.save_command(final_prompt, mode, name, start)

            # Handle cloud mode vs local mode
            if mode.lower() == "cloud":
                # Cloud mode: generate and display deployment instructions
                print_info("\n🌤️  Cloud Mode: Generating deployment instructions...")
                
                cloud_detector = CloudDetector()
                available_platforms = cloud_detector.get_available_platforms()
                
                if available_platforms:
                    print_success(f"Detected cloud platforms: {', '.join(available_platforms)}")
                else:
                    print_warning("No cloud CLIs detected. Instructions will include all supported platforms.")
                    print_info("Available platforms: AWS, GCP, Docker Hub")
                
                instruction_generator = CloudInstructionGenerator()
                instructions = instruction_generator.generate_instructions(
                    stack_config, available_platforms
                )
                
                # Display instructions
                print_info("\n" + "=" * 80)
                print_header("Cloud Deployment Instructions")
                print_info("=" * 80 + "\n")
                print_info(instructions)
                print_info("\n" + "=" * 80)
                
                # Save instructions to file
                from pathlib import Path
                project_name = name or stack_config.name
                output_dir = Path(".")
                instructions_file = output_dir / f"{project_name}-cloud-deployment.md"
                
                instructions_file.write_text(instructions)
                print_success(f"\n✅ Cloud deployment instructions saved to: {instructions_file.absolute()}")
                print_info("\nNext steps:")
                print_info(f"  1. Review the instructions in {instructions_file.name}")
                print_info("  2. Follow the platform-specific deployment steps")
                print_info("  3. Configure your cloud provider credentials")
            else:
                # Local mode: scaffold project as usual
                print_info("\nStarting project scaffolding...")
                scaffolder = ScaffoldingEngine(project_name=name)

                with create_progress_bar() as progress:
                    task = progress.add_task(
                        "[cyan]Generating project structure...", total=None
                    )
                    project_path = scaffolder.scaffold(stack_config)
                    progress.update(task, completed=True)

                print_success(f"\n✅ Project ready at: {project_path}")

                # Optionally start services
                if start:
                    print_info("\nStarting services...")
                    from pathlib import Path

                    env_manager = EnvironmentManager(Path(project_path))
                    if env_manager.start():
                        print_success("Services started successfully!")
                    else:
                        print_warning("Failed to start services. You can start them manually with 'make up'")
                else:
                    print_info("\nNext steps:")
                    print_info("  1. Start all services (with automatic port conflict resolution):")
                    print_info(f"     getupandrun start {project_path}")
                    print_info("  2. View service status:")
                    print_info(f"     getupandrun status {project_path}")
                    print_info("  3. View service logs (optional):")
                    print_info(f"     cd {project_path} && make logs")

                # Print Git commands
                print_info("")
                from pathlib import Path

                GitHelper.print_git_commands(Path(project_path), name or stack_config.name)

        except GetUpAndRunError as e:
            crash_logger.log_error(
                e,
                context={
                    "command": "main",
                    "prompt": prompt or "N/A",
                    "template": template or "N/A",
                    "mode": mode,
                },
            )
            e.exit()
        except ValueError as e:
            crash_logger.log_error(
                e,
                context={
                    "command": "main",
                    "error_type": "ValueError",
                    "prompt": prompt or "N/A",
                },
            )
            handle_error(e, ErrorCode.INVALID_CONFIG)
        except Exception as e:
            crash_logger.log_error(
                e,
                context={
                    "command": "main",
                    "error_type": type(e).__name__,
                    "prompt": prompt or "N/A",
                },
            )
            handle_error(e, ErrorCode.UNKNOWN_ERROR)


@cli.command()
def help() -> None:
    """Show detailed help information and usage guide."""
    help_command()


@cli.command()
def version() -> None:
    """Show version information."""
    version_command()


@cli.command()
def last() -> None:
    """Re-run the last command."""
    last_command()


@cli.command()
def history() -> None:
    """Show command history."""
    history_command()


@cli.command()
@click.option("--search", "-s", type=str, help="Search templates by keyword")
def templates(search: Optional[str]) -> None:
    """List available templates."""
    templates_command(search)


@cli.command()
def doctor() -> None:
    """Run diagnostic checks on your system."""
    doctor_command()


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False))
@click.option("--detach", "-d", is_flag=True, default=True, help="Run in detached mode")
def start(project_path: str, detach: bool) -> None:
    """Start Docker Compose services for a project."""
    start_command(project_path, detach)


@cli.command()
@click.argument("project_path", required=False, type=click.Path(exists=True, file_okay=False))
@click.option("--all", "-a", is_flag=True, help="Stop all GetUpAndRun projects")
def stop(project_path: Optional[str], all: bool) -> None:
    """Stop Docker Compose services for a project."""
    if all:
        stop_all_command()
    elif project_path:
        stop_command(project_path)
    else:
        print_error("Error: Either provide a project path or use --all flag")
        print_info("Usage: getupandrun stop <project_path> or getupandrun stop --all")
        sys.exit(2)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--volumes", "-v", is_flag=True, default=False, help="Also remove volumes"
)
def teardown(project_path: str, volumes: bool) -> None:
    """Tear down Docker Compose services for a project."""
    teardown_command(project_path, volumes)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--volumes", "-v", is_flag=True, default=False, help="Also remove volumes"
)
def down(project_path: str, volumes: bool) -> None:
    """Clean shutdown command (stops and removes containers with verification)."""
    down_command(project_path, volumes)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompt"
)
def reset(project_path: str, yes: bool) -> None:
    """Reset project by removing all containers, volumes, and project files."""
    reset_command(project_path, yes)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False))
def restart(project_path: str) -> None:
    """Restart Docker Compose services for a project."""
    restart_command(project_path)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False))
def status(project_path: str) -> None:
    """Show status of Docker Compose services for a project."""
    status_command(project_path)


@cli.command()
def update() -> None:
    """Check for updates and notify if a new version is available."""
    from getupandrun.cli.commands import update_command
    update_command()


@cli.command()
def install_completion() -> None:
    """Install shell completion for GetUpAndRun."""
    from getupandrun.cli.commands import install_completion_command
    install_completion_command()


@cli.command()
@click.option(
    "--port", "-p", type=int, default=3000, help="Port to run the UI server on"
)
def ui(port: int) -> None:
    """Start the Next.js web UI."""
    from getupandrun.cli.ui_command import ui_command
    ui_command(port)


if __name__ == "__main__":
    cli()
