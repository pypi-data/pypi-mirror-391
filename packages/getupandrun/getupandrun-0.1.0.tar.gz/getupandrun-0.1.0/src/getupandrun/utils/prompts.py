"""Interactive prompt utilities for CLI."""

from typing import Any, Callable, Optional

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from getupandrun.utils.logger import get_console

console = get_console()


def ask_question(
    question: str,
    default: Optional[str] = None,
    type: type = str,
    validator: Optional[Callable[[Any], bool]] = None,
) -> Any:
    """
    Ask an interactive question with validation.

    Args:
        question: Question to ask
        default: Default value if user presses Enter
        type: Type to convert input to
        validator: Optional validation function

    Returns:
        User's answer (converted to type)
    """
    while True:
        try:
            if default:
                prompt_text = f"{question} [{default}]: "
            else:
                prompt_text = f"{question}: "

            answer = click.prompt(prompt_text, default=default, type=type)

            if validator and not validator(answer):
                console.print("[error]✗[/error] Invalid input. Please try again.")
                continue

            return answer
        except click.Abort:
            console.print("\n[warning]⚠[/warning] Aborted by user.")
            raise
        except Exception as e:
            console.print(f"[error]✗[/error] Error: {e}. Please try again.")


def ask_yes_no(question: str, default: bool = True) -> bool:
    """
    Ask a yes/no question.

    Args:
        question: Question to ask
        default: Default value

    Returns:
        True for yes, False for no
    """
    return Confirm.ask(f"[prompt]?[/prompt] {question}", default=default, console=console)


def ask_choice(
    question: str,
    choices: list[str],
    default: Optional[str] = None,
) -> str:
    """
    Ask user to choose from a list of options.

    Args:
        question: Question to ask
        choices: List of choices
        default: Default choice

    Returns:
        Selected choice
    """
    console.print(f"[prompt]?[/prompt] {question}")
    for i, choice in enumerate(choices, 1):
        marker = "→" if choice == default else " "
        console.print(f"  {marker} [{i}] {choice}")

    while True:
        try:
            if default:
                prompt_text = f"Select [1-{len(choices)}] (default: {default}): "
            else:
                prompt_text = f"Select [1-{len(choices)}]: "

            answer = click.prompt(prompt_text, default=default, type=str)

            # Try to parse as number
            try:
                index = int(answer) - 1
                if 0 <= index < len(choices):
                    return choices[index]
            except ValueError:
                pass

            # Try to match by name
            if answer in choices:
                return answer

            console.print(
                f"[error]✗[/error] Invalid choice. Please enter a number (1-{len(choices)}) or the choice name."
            )
        except click.Abort:
            console.print("\n[warning]⚠[/warning] Aborted by user.")
            raise


def ask_multiline(question: str, default: Optional[str] = None) -> str:
    """
    Ask for multiline input (press Ctrl+D or Ctrl+Z to finish).

    Args:
        question: Question to ask
        default: Default value

    Returns:
        Multiline input
    """
    console.print(f"[prompt]?[/prompt] {question}")
    if default:
        console.print(f"[dim](Press Enter twice or Ctrl+D to finish, default shown below)[/dim]")
        console.print(f"[dim]Default: {default}[/dim]")

    lines = []
    try:
        while True:
            try:
                line = input()
                if not line and lines:  # Empty line after content means done
                    break
                lines.append(line)
            except EOFError:
                break
    except KeyboardInterrupt:
        console.print("\n[warning]⚠[/warning] Aborted by user.")
        raise

    result = "\n".join(lines).strip()
    return result if result else (default or "")


def detect_config_mismatches(original_prompt: str, stack_config: "StackConfig") -> list[dict]:
    """
    Detect potential mismatches between prompt and generated config.

    Args:
        original_prompt: Original user prompt
        stack_config: Generated stack configuration

    Returns:
        List of detected mismatches (empty if none)
    """
    from getupandrun.gpt.integration import StackConfig

    mismatches = []
    prompt_lower = original_prompt.lower()

    # Common framework mappings
    framework_keywords = {
        "django": ["django"],
        "fastapi": ["fastapi", "fast api"],
        "flask": ["flask"],
        "react": ["react"],
        "vue": ["vue"],
        "angular": ["angular"],
        "node": ["node", "nodejs", "node.js", "express"],
        "postgres": ["postgres", "postgresql"],
        "mysql": ["mysql"],
        "mongodb": ["mongo", "mongodb"],
        "redis": ["redis"],
        "sqlite": ["sqlite"],
    }

    # Check each service for mismatches
    for service in stack_config.services:
        service_framework = service.get("framework", "").lower()
        service_type = service.get("type", "").lower()

        # Determine which keywords are relevant for this service type
        relevant_keywords = []
        if service_type == "backend":
            relevant_keywords = ["django", "fastapi", "flask"]
        elif service_type == "frontend":
            relevant_keywords = ["react", "vue", "angular"]
        elif service_type == "database":
            relevant_keywords = ["postgres", "mysql", "mongodb", "sqlite"]
        elif service_type == "cache":
            relevant_keywords = ["redis"]

        # Check if any relevant keyword is mentioned in prompt
        for keyword in relevant_keywords:
            if keyword in framework_keywords:
                variants = framework_keywords[keyword]
                # If keyword is mentioned in prompt
                if any(variant in prompt_lower for variant in variants):
                    # But not in the detected framework
                    if keyword not in service_framework and service_framework not in keyword:
                        mismatches.append({
                            "service": service.get("name"),
                            "type": service_type,
                            "expected": keyword,
                            "detected": service_framework,
                        })
                        break  # Only flag one mismatch per service

    return mismatches


def confirm_if_uncertain(
    original_prompt: str, stack_config: "StackConfig", gpt_client: Optional[Any] = None
) -> tuple["StackConfig", str]:
    """
    Only ask for confirmation if mismatches are detected.
    If user rejects mismatched services, allows re-entering prompt.

    Args:
        original_prompt: Original user prompt
        stack_config: Generated stack configuration
        gpt_client: Optional GPT client for re-interpretation

    Returns:
        Tuple of (confirmed stack configuration, final prompt used)
    """
    from getupandrun.gpt.integration import StackConfig
    from getupandrun.utils.logger import print_table

    current_prompt = original_prompt
    current_config = stack_config
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        # Detect mismatches
        mismatches = detect_config_mismatches(current_prompt, current_config)
        mismatch_services = {m["service"] for m in mismatches}

        # If no mismatches, proceed without asking
        if not mismatches:
            return current_config, current_prompt

        # If mismatches found, ask for confirmation
        console.print("\n[warning]⚠ Potential mismatches detected:[/warning]")

        for mismatch in mismatches:
            console.print(
                f"  • {mismatch['service']}: Expected {mismatch['expected']}, "
                f"but detected {mismatch['detected']}"
            )

        console.print("\n[bold]Detected Stack Configuration:[/bold]")
        headers = ["Service", "Type", "Framework"]
        rows = []
        for service in current_config.services:
            rows.append([
                service.get("name", "service"),
                service.get("type", "other"),
                service.get("framework", ""),
            ])
        print_table(headers, rows)

        console.print("\n[bold]Please confirm each service:[/bold]")

        confirmed_services = []
        rejected_mismatched = False

        for service in current_config.services:
            service_name = service.get("name", "service")
            service_type = service.get("type", "other")
            framework = service.get("framework", "")

            # Format question
            if service_type == "frontend":
                question = f"{framework.capitalize()} frontend?"
            elif service_type == "backend":
                question = f"{framework.capitalize()} backend?"
            elif service_type == "database":
                question = f"{framework.capitalize()} database?"
            elif service_type == "cache":
                question = f"{framework.capitalize()} cache?"
            else:
                question = f"{framework.capitalize()} {service_type}?"

            if ask_yes_no(question, default=True):
                confirmed_services.append(service)
            else:
                console.print(f"[dim]Skipping {service_name}[/dim]")
                # Check if this was a mismatched service
                if service_name in mismatch_services:
                    rejected_mismatched = True

        if not confirmed_services:
            raise ValueError("No services confirmed. Aborting.")

        # If user rejected a mismatched service, offer to re-enter prompt
        if rejected_mismatched and gpt_client:
            if ask_yes_no(
                "Would you like to re-enter your prompt to get a better interpretation?",
                default=True,
            ):
                retry_count += 1
                console.print("\n[bold]Re-enter your stack description:[/bold]")
                new_prompt = ask_question(
                    "Describe your desired stack",
                    validator=lambda x: len(x.strip()) > 0,
                )
                current_prompt = new_prompt

                # Re-interpret with GPT
                console.print("Re-interpreting with GPT...")
                from getupandrun.utils.logger import create_progress_bar

                with create_progress_bar() as progress:
                    task = progress.add_task(
                        "[cyan]Interpreting your prompt with GPT...", total=None
                    )
                    current_config = gpt_client.interpret_prompt(new_prompt)
                    progress.update(task, completed=True)

                console.print(f"Project: {current_config.name}")
                console.print(f"Description: {current_config.description}")
                console.print(f"Services: {len(current_config.services)}")
                continue  # Loop back to check for mismatches again
            else:
                # User doesn't want to re-enter, proceed with confirmed services
                break
        else:
            # No rejected mismatches or no GPT client, proceed
            break

    # Return modified config
    return (
        StackConfig(
            name=current_config.name,
            description=current_config.description,
            services=confirmed_services,
            dependencies={
                k: v
                for k, v in current_config.dependencies.items()
                if k in [s.get("name") for s in confirmed_services]
            },
            ports={
                k: v
                for k, v in current_config.ports.items()
                if k in [s.get("name") for s in confirmed_services]
            },
        ),
        current_prompt,
    )

