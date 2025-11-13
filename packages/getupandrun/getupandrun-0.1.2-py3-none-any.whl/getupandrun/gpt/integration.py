"""OpenAI GPT integration for interpreting natural language stack descriptions."""

import json
import os
from typing import Any, Optional

from openai import OpenAI
from openai.types.chat import ChatCompletion

from getupandrun.utils.errors import ErrorCode, GetUpAndRunError
from getupandrun.utils.logger import print_error, print_info, print_warning


class StackConfig:
    """Structured configuration for a development stack."""

    def __init__(
        self,
        name: str,
        description: str,
        services: list[dict[str, Any]],
        dependencies: dict[str, list[str]],
        ports: dict[str, int],
    ) -> None:
        """
        Initialize stack configuration.

        Args:
            name: Project name
            description: Project description
            services: List of service definitions
            dependencies: Dependency mapping (service -> dependencies)
            ports: Port mapping (service -> port)
        """
        self.name = name
        self.description = description
        self.services = services
        self.dependencies = dependencies
        self.ports = ports

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StackConfig":
        """
        Create StackConfig from dictionary.

        Args:
            data: Dictionary containing stack configuration

        Returns:
            StackConfig instance
        """
        return cls(
            name=data.get("name", "project"),
            description=data.get("description", ""),
            services=data.get("services", []),
            dependencies=data.get("dependencies", {}),
            ports=data.get("ports", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert StackConfig to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "description": self.description,
            "services": self.services,
            "dependencies": self.dependencies,
            "ports": self.ports,
        }


class GPTClient:
    """Client for interacting with OpenAI GPT API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize GPT client.

        Args:
            api_key: OpenAI API key. If not provided, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise GetUpAndRunError(
                "OpenAI API key not found",
                error_code=ErrorCode.MISSING_API_KEY,
                suggestion="Set your OpenAI API key: export OPENAI_API_KEY='your-key'",
            )
        self.client = OpenAI(api_key=self.api_key)

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the instruction schema.

        Returns:
            System prompt string
        """
        return """You are a development environment generator. Your task is to interpret natural language descriptions of software stacks and generate structured JSON configurations.

Generate a JSON object with the following structure:
{
  "name": "project-name",
  "description": "Brief description of the project",
  "services": [
    {
      "name": "service-name",
      "type": "frontend|backend|database|cache|other",
      "framework": "react|vue|angular|nextjs|next.js|nuxtjs|nuxt.js|node|express|nestjs|nest.js|python|django|fastapi|flask|postgres|postgresql|mysql|mongodb|mongo|redis|memcached|sqlite|rabbitmq|kafka|etc",
      "version": "version-string",
      "dockerfile": true/false,
      "dependencies": ["dependency1", "dependency2"]
    }
  ],
  "dependencies": {
    "service-name": ["npm", "pip", "apt", etc]
  },
  "ports": {
    "service-name": port-number
  }
}

Guidelines:
- Use kebab-case for project and service names
- Assign appropriate default ports (3000 for frontend, 8000 for backend, 5432 for postgres, 6379 for redis)
- Include all necessary services (frontend, backend, database, etc.)
- Specify framework versions when known
- Mark services that need Dockerfiles
- List package managers needed for each service
- IMPORTANT: If the user mentions "Django", use "django" as the framework (not "python")
- IMPORTANT: If the user mentions "FastAPI", use "fastapi" as the framework (not "python")
- IMPORTANT: If the user mentions "Flask", use "flask" as the framework (not "python")
- IMPORTANT: If the user mentions "Express" or "Node.js backend", use "express" or "node" as the framework
- IMPORTANT: If the user mentions "NestJS" or "Nest.js", use "nestjs" as the framework
- IMPORTANT: If the user mentions "React frontend", use "react" as the framework
- IMPORTANT: If the user mentions "Vue frontend", use "vue" as the framework
- IMPORTANT: If the user mentions "Angular frontend", use "angular" as the framework
- IMPORTANT: If the user mentions "Next.js" or "NextJS", use "nextjs" as the framework
- IMPORTANT: If the user mentions "Nuxt.js" or "NuxtJS", use "nuxtjs" as the framework
- IMPORTANT: If the user mentions "MySQL database", use "mysql" as the framework
- IMPORTANT: If the user mentions "MongoDB" or "Mongo", use "mongodb" as the framework
- IMPORTANT: If the user mentions "Memcached", use "memcached" as the framework
- IMPORTANT: If the user mentions "RabbitMQ", use "rabbitmq" as the framework
- IMPORTANT: If the user mentions "Kafka", use "kafka" as the framework
- NOTE: Currently supported frameworks: React, Vue, Angular, Next.js, Nuxt.js (frontend), Express/Node.js, NestJS, Django, FastAPI, Flask (backend), PostgreSQL, MySQL, MongoDB, Redis, Memcached, SQLite (database/cache), RabbitMQ, Kafka (message queues)
- NOTE: Desktop frameworks (Electron, Tauri) are not supported - this tool generates web applications with Docker Compose orchestration
"""

    def _get_user_prompt(self, description: str) -> str:
        """
        Format user description into prompt.

        Args:
            description: Natural language description of desired stack

        Returns:
            Formatted user prompt
        """
        return f"""Generate a development stack configuration for the following description:

{description}

Provide only valid JSON, no additional text or markdown formatting."""

    def interpret_prompt(
        self, description: str, model: str = "gpt-4o-mini"
    ) -> StackConfig:
        """
        Interpret natural language description and generate stack configuration.

        Args:
            description: Natural language description of desired stack
            model: OpenAI model to use (default: gpt-4o-mini)

        Returns:
            StackConfig object

        Raises:
            ValueError: If GPT response is invalid or cannot be parsed
            Exception: For API errors
        """
        print_info(f"Interpreting stack description with {model}...")

        try:
            response: ChatCompletion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": self._get_user_prompt(description)},
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from GPT API")

            print_info("Parsing GPT response...")
            config_dict = self._parse_response(content)
            stack_config = StackConfig.from_dict(config_dict)

            print_info(f"Successfully generated configuration for: {stack_config.name}")
            return stack_config

        except json.JSONDecodeError as e:
            raise GetUpAndRunError(
                "Failed to parse GPT response",
                error_code=ErrorCode.GPT_PARSE_ERROR,
                details=str(e),
                suggestion="Try running the command again. If the issue persists, check your OpenAI API key.",
            ) from e
        except Exception as e:
            raise GetUpAndRunError(
                "Error calling GPT API",
                error_code=ErrorCode.GPT_API_ERROR,
                details=str(e),
                suggestion="Check your internet connection and OpenAI API key.",
            ) from e

    def _parse_response(self, content: str) -> dict[str, Any]:
        """
        Parse GPT response content into configuration dictionary.

        Args:
            content: Raw response content from GPT

        Returns:
            Parsed configuration dictionary

        Raises:
            ValueError: If response cannot be parsed
        """
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            config = json.loads(content)
            self._validate_config(config)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in GPT response: {e}") from e

    def _validate_config(self, config: dict[str, Any]) -> None:
        """
        Validate configuration structure.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = ["name", "services"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required key in configuration: {key}")

        if not isinstance(config["services"], list):
            raise ValueError("'services' must be a list")

        if len(config["services"]) == 0:
            raise ValueError("At least one service must be defined")

        # Validate each service
        for service in config["services"]:
            if not isinstance(service, dict):
                raise ValueError("Each service must be a dictionary")
            if "name" not in service:
                raise ValueError("Each service must have a 'name' field")

        # Set defaults for optional fields
        if "description" not in config:
            config["description"] = ""
        if "dependencies" not in config:
            config["dependencies"] = {}
        if "ports" not in config:
            config["ports"] = {}

