"""Structured error handling for GetUpAndRun."""

import sys
from enum import IntEnum
from typing import Optional

from getupandrun.utils.logger import print_error, print_info, print_warning


class ErrorCode(IntEnum):
    """Structured error codes for GetUpAndRun."""

    # Success
    SUCCESS = 0

    # Configuration errors (1-99)
    MISSING_API_KEY = 1
    INVALID_CONFIG = 2
    INVALID_TEMPLATE = 3
    INVALID_PROMPT = 4

    # GPT/API errors (100-199)
    GPT_API_ERROR = 100
    GPT_PARSE_ERROR = 101
    GPT_EMPTY_RESPONSE = 102

    # Scaffolding errors (200-299)
    SCAFFOLD_FAILED = 200
    FILE_WRITE_ERROR = 201
    DIRECTORY_CREATE_ERROR = 202

    # Docker/Environment errors (300-399)
    DOCKER_NOT_RUNNING = 300
    DOCKER_COMPOSE_ERROR = 301
    PORT_CONFLICT = 302
    CONTAINER_START_FAILED = 303
    CONTAINER_STOP_FAILED = 304

    # System errors (400-499)
    MISSING_DEPENDENCY = 400
    PERMISSION_ERROR = 401
    DISK_SPACE_ERROR = 402

    # Usage errors (500-599)
    INVALID_ARGUMENT = 500
    MISSING_ARGUMENT = 501
    INVALID_PATH = 502

    # Unknown errors (900-999)
    UNKNOWN_ERROR = 900


class GetUpAndRunError(Exception):
    """Base exception for GetUpAndRun with structured error codes."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """
        Initialize error.

        Args:
            message: User-friendly error message
            error_code: Structured error code
            details: Additional technical details
            suggestion: Suggested fix or action
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details
        self.suggestion = suggestion

    def print_error(self) -> None:
        """Print formatted error message."""
        print_error(f"[{self.error_code.value}] {self.message}")

        if self.details:
            print_info(f"Details: {self.details}")

        if self.suggestion:
            print_warning(f"💡 Suggestion: {self.suggestion}")

    def exit(self) -> None:
        """Print error and exit with appropriate code."""
        self.print_error()
        sys.exit(self.error_code.value)


def handle_error(error: Exception, error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR) -> None:
    """
    Handle an exception and exit gracefully.

    Args:
        error: Exception to handle
        error_code: Error code to use
    """
    if isinstance(error, GetUpAndRunError):
        error.exit()

    # Convert generic exceptions to structured errors
    error_msg = str(error)
    suggestion = None

    # Provide helpful suggestions based on error type
    if "API key" in error_msg or "OPENAI_API_KEY" in error_msg:
        error_code = ErrorCode.MISSING_API_KEY
        suggestion = "Set your OpenAI API key: export OPENAI_API_KEY='your-key'"
    elif "Docker" in error_msg or "docker" in error_msg:
        error_code = ErrorCode.DOCKER_NOT_RUNNING
        suggestion = "Make sure Docker is running: docker ps"
    elif "Permission" in error_msg or "permission" in error_msg:
        error_code = ErrorCode.PERMISSION_ERROR
        suggestion = "Check file permissions or run with appropriate privileges"
    elif "No space" in error_msg or "disk" in error_msg.lower():
        error_code = ErrorCode.DISK_SPACE_ERROR
        suggestion = "Free up disk space and try again"

    structured_error = GetUpAndRunError(
        message=error_msg,
        error_code=error_code,
        details=str(error),
        suggestion=suggestion,
    )
    structured_error.exit()

