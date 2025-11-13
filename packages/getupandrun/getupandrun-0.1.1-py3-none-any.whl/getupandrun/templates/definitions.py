"""Predefined template definitions for common stacks."""

from typing import Any

from getupandrun.gpt.integration import StackConfig


# Template definitions
TEMPLATES: dict[str, dict[str, Any]] = {
    "react-node-postgres": {
        "name": "React + Node.js + Postgres",
        "description": "Full-stack web application with React frontend, Node.js/Express backend, and PostgreSQL database",
        "services": [
            {
                "name": "frontend",
                "type": "frontend",
                "framework": "react",
                "version": "18.2.0",
                "dockerfile": True,
            },
            {
                "name": "backend",
                "type": "backend",
                "framework": "node",
                "version": "20",
                "dockerfile": True,
            },
            {
                "name": "database",
                "type": "database",
                "framework": "postgres",
                "version": "15",
                "dockerfile": True,
            },
        ],
        "dependencies": {
            "frontend": ["npm"],
            "backend": ["npm"],
            "database": [],
        },
        "ports": {
            "frontend": 3000,
            "backend": 8000,
            "database": 5432,
        },
    },
    "fastapi-redis": {
        "name": "FastAPI + Redis",
        "description": "Python FastAPI backend with Redis cache",
        "services": [
            {
                "name": "backend",
                "type": "backend",
                "framework": "fastapi",
                "version": "0.104.1",
                "dockerfile": True,
            },
            {
                "name": "cache",
                "type": "cache",
                "framework": "redis",
                "version": "7",
                "dockerfile": True,
            },
        ],
        "dependencies": {
            "backend": ["pip"],
            "cache": [],
        },
        "ports": {
            "backend": 8000,
            "cache": 6379,
        },
    },
    "django-postgres": {
        "name": "Django + Postgres",
        "description": "Django web application with PostgreSQL database",
        "services": [
            {
                "name": "backend",
                "type": "backend",
                "framework": "django",
                "version": "4.2",
                "dockerfile": True,
            },
            {
                "name": "database",
                "type": "database",
                "framework": "postgres",
                "version": "15",
                "dockerfile": True,
            },
        ],
        "dependencies": {
            "backend": ["pip"],
            "database": [],
        },
        "ports": {
            "backend": 8000,
            "database": 5432,
        },
    },
    "vue-node-mongodb": {
        "name": "Vue + Node.js + MongoDB",
        "description": "Vue.js frontend with Node.js backend and MongoDB database",
        "services": [
            {
                "name": "frontend",
                "type": "frontend",
                "framework": "vue",
                "version": "3",
                "dockerfile": True,
            },
            {
                "name": "backend",
                "type": "backend",
                "framework": "node",
                "version": "20",
                "dockerfile": True,
            },
            {
                "name": "database",
                "type": "database",
                "framework": "mongodb",
                "version": "7",
                "dockerfile": True,
            },
        ],
        "dependencies": {
            "frontend": ["npm"],
            "backend": ["npm"],
            "database": [],
        },
        "ports": {
            "frontend": 3000,
            "backend": 8000,
            "database": 27017,
        },
    },
    "nextjs-postgres": {
        "name": "Next.js + Postgres",
        "description": "Next.js full-stack application with PostgreSQL database",
        "services": [
            {
                "name": "frontend",
                "type": "frontend",
                "framework": "nextjs",
                "version": "14",
                "dockerfile": True,
            },
            {
                "name": "database",
                "type": "database",
                "framework": "postgres",
                "version": "15",
                "dockerfile": True,
            },
        ],
        "dependencies": {
            "frontend": ["npm"],
            "database": [],
        },
        "ports": {
            "frontend": 3000,
            "database": 5432,
        },
    },
    "flask-redis": {
        "name": "Flask + Redis",
        "description": "Flask Python backend with Redis cache",
        "services": [
            {
                "name": "backend",
                "type": "backend",
                "framework": "flask",
                "version": "3.0",
                "dockerfile": True,
            },
            {
                "name": "cache",
                "type": "cache",
                "framework": "redis",
                "version": "7",
                "dockerfile": True,
            },
        ],
        "dependencies": {
            "backend": ["pip"],
            "cache": [],
        },
        "ports": {
            "backend": 8000,
            "cache": 6379,
        },
    },
}


def get_template(key: str) -> StackConfig:
    """
    Get a template by key.

    Args:
        key: Template key (e.g., "react-node-postgres")

    Returns:
        StackConfig instance

    Raises:
        KeyError: If template not found
    """
    if key not in TEMPLATES:
        raise KeyError(f"Template '{key}' not found")

    template_data = TEMPLATES[key]
    return StackConfig.from_dict(template_data)


def list_templates() -> list[dict[str, str]]:
    """
    List all available templates.

    Returns:
        List of template info dictionaries with 'key', 'name', and 'description'
    """
    return [
        {
            "key": key,
            "name": template["name"],
            "description": template["description"],
        }
        for key, template in TEMPLATES.items()
    ]


def search_templates(query: str) -> list[dict[str, str]]:
    """
    Search templates by name or description.

    Args:
        query: Search query

    Returns:
        List of matching template info dictionaries
    """
    query_lower = query.lower()
    results = []

    for key, template in TEMPLATES.items():
        name = template["name"].lower()
        description = template["description"].lower()

        if query_lower in name or query_lower in description or query_lower in key:
            results.append(
                {
                    "key": key,
                    "name": template["name"],
                    "description": template["description"],
                }
            )

    return results

