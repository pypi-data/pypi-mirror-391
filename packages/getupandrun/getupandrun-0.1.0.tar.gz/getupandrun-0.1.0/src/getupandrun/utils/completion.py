"""Shell completion support for GetUpAndRun CLI."""

import click


def get_template_completions(ctx: click.Context, param: click.Parameter, incomplete: str) -> list[str]:
    """Get template name completions."""
    from getupandrun.templates.manager import TemplateManager

    try:
        template_manager = TemplateManager()
        templates = template_manager.list_templates()
        return [t["key"] for t in templates if t["key"].startswith(incomplete)]
    except Exception:
        return []


def get_mode_completions(ctx: click.Context, param: click.Parameter, incomplete: str) -> list[str]:
    """Get mode completions."""
    modes = ["local", "cloud"]
    return [m for m in modes if m.startswith(incomplete)]

