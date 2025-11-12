"""Comprehensive validation and type checking system for the DeepSeek CLI."""

from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

import jsonschema
from pydantic import BaseModel, Field, ValidationError, validator


T = TypeVar("T")


class ValidationLevel(Enum):
    """Levels of validation strictness."""
    NONE = "none"  # No validation
    BASIC = "basic"  # Basic type checking
    STANDARD = "standard"  # Standard validation with schemas
    STRICT = "strict"  # Strict validation with all constraints


class ValidationType(Enum):
    """Types of validation to perform."""
    TYPE = "type"
    RANGE = "range"
    PATTERN = "pattern"
    SCHEMA = "schema"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """A single validation rule."""
    name: str
    type: ValidationType
    validator: Callable[[Any], bool]
    error_message: str
    level: ValidationLevel = ValidationLevel.STANDARD


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_value: Optional[Any] = None

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


class TypeValidator:
    """Advanced type validation with support for complex types."""

    @staticmethod
    def validate_type(value: Any, expected_type: Type) -> bool:
        """Validate that value matches expected type."""
        # Handle None/Optional
        if value is None:
            origin = get_origin(expected_type)
            if origin is Union:
                args = get_args(expected_type)
                return type(None) in args
            return False

        # Handle generic types
        origin = get_origin(expected_type)
        if origin is not None:
            return TypeValidator._validate_generic(value, origin, get_args(expected_type))

        # Simple type check
        return isinstance(value, expected_type)

    @staticmethod
    def _validate_generic(value: Any, origin: Type, args: Tuple) -> bool:
        """Validate generic types like List[str], Dict[str, int], etc."""
        if origin is list:
            if not isinstance(value, list):
                return False
            if args:
                item_type = args[0]
                return all(TypeValidator.validate_type(item, item_type) for item in value)
            return True

        if origin is dict:
            if not isinstance(value, dict):
                return False
            if len(args) == 2:
                key_type, value_type = args
                return all(
                    TypeValidator.validate_type(k, key_type) and
                    TypeValidator.validate_type(v, value_type)
                    for k, v in value.items()
                )
            return True

        if origin is Union:
            return any(TypeValidator.validate_type(value, arg) for arg in args)

        if origin is tuple:
            if not isinstance(value, tuple):
                return False
            if args:
                if len(args) == 2 and args[1] is ...:
                    # Tuple[type, ...]
                    return all(TypeValidator.validate_type(item, args[0]) for item in value)
                # Tuple[type1, type2, ...]
                return len(value) == len(args) and all(
                    TypeValidator.validate_type(v, t) for v, t in zip(value, args)
                )
            return True

        if origin is set:
            if not isinstance(value, set):
                return False
            if args:
                item_type = args[0]
                return all(TypeValidator.validate_type(item, item_type) for item in value)
            return True

        return isinstance(value, origin)


class PatternValidator:
    """Validation using regular expressions."""

    # Common patterns
    PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "url": r"^https?://[^\s/$.?#].[^\s]*$",
        "ipv4": r"^(\d{1,3}\.){3}\d{1,3}$",
        "ipv6": r"^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$",
        "uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        "semver": r"^\d+\.\d+\.\d+(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$",
        "alphanum": r"^[a-zA-Z0-9]+$",
        "slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    }

    @staticmethod
    def validate(value: str, pattern: Union[str, re.Pattern]) -> bool:
        """Validate string against pattern."""
        if isinstance(pattern, str):
            if pattern in PatternValidator.PATTERNS:
                pattern = PatternValidator.PATTERNS[pattern]
            pattern = re.compile(pattern)
        return bool(pattern.match(value))


class RangeValidator:
    """Validation for numeric ranges."""

    @staticmethod
    def validate_range(
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        exclusive_min: bool = False,
        exclusive_max: bool = False
    ) -> bool:
        """Validate that value is within specified range."""
        if min_value is not None:
            if exclusive_min and value <= min_value:
                return False
            if not exclusive_min and value < min_value:
                return False

        if max_value is not None:
            if exclusive_max and value >= max_value:
                return False
            if not exclusive_max and value > max_value:
                return False

        return True


class SchemaValidator:
    """JSON Schema validation."""

    def __init__(self):
        self._schemas: Dict[str, Dict] = {}

    def register_schema(self, name: str, schema: Dict) -> None:
        """Register a JSON schema."""
        self._schemas[name] = schema

    def validate(self, data: Any, schema: Union[str, Dict]) -> ValidationResult:
        """Validate data against schema."""
        if isinstance(schema, str):
            if schema not in self._schemas:
                return ValidationResult(
                    valid=False,
                    errors=[f"Schema '{schema}' not found"]
                )
            schema = self._schemas[schema]

        try:
            jsonschema.validate(data, schema)
            return ValidationResult(valid=True)
        except jsonschema.ValidationError as e:
            return ValidationResult(
                valid=False,
                errors=[str(e)]
            )


class InputSanitizer:
    """Sanitize and normalize inputs."""

    @staticmethod
    def sanitize_path(path: str) -> str:
        """Sanitize file path."""
        # Remove null bytes
        path = path.replace("\x00", "")

        # Normalize path separators
        path = path.replace("\\", "/")

        # Remove redundant separators
        while "//" in path:
            path = path.replace("//", "/")

        # Prevent directory traversal
        parts = []
        for part in path.split("/"):
            if part == "..":
                if parts and parts[-1] != "..":
                    parts.pop()
            elif part and part != ".":
                parts.append(part)

        return "/".join(parts)

    @staticmethod
    def sanitize_command(command: str) -> str:
        """Sanitize shell command."""
        # Remove dangerous characters
        dangerous = [";", "|", "&", "`", "$", "(", ")", "{", "}", "[", "]", "<", ">", "\n", "\r"]
        for char in dangerous:
            command = command.replace(char, "")

        return command.strip()

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML/text to prevent injection."""
        import html
        return html.escape(text)

    @staticmethod
    def sanitize_sql(value: str) -> str:
        """Basic SQL sanitization."""
        # This is a basic implementation - use parameterized queries in production
        return value.replace("'", "''").replace(";", "")


# Pydantic models for complex validation

class FilePathModel(BaseModel):
    """Model for file path validation."""
    path: str
    must_exist: bool = False
    must_be_file: bool = False
    must_be_dir: bool = False
    allowed_extensions: Optional[List[str]] = None

    @validator("path")
    def validate_path(cls, v):
        """Validate and sanitize path."""
        v = InputSanitizer.sanitize_path(v)
        return v

    def validate(self) -> ValidationResult:
        """Perform full validation."""
        result = ValidationResult(valid=True, sanitized_value=self.path)
        path_obj = Path(self.path)

        if self.must_exist and not path_obj.exists():
            result.valid = False
            result.errors.append(f"Path does not exist: {self.path}")

        if self.must_be_file and not path_obj.is_file():
            result.valid = False
            result.errors.append(f"Path is not a file: {self.path}")

        if self.must_be_dir and not path_obj.is_dir():
            result.valid = False
            result.errors.append(f"Path is not a directory: {self.path}")

        if self.allowed_extensions:
            ext = path_obj.suffix.lower()
            if ext not in self.allowed_extensions:
                result.valid = False
                result.errors.append(f"Invalid extension {ext}. Allowed: {self.allowed_extensions}")

        return result


class CommandModel(BaseModel):
    """Model for shell command validation."""
    command: str
    allowed_commands: Optional[List[str]] = None
    forbidden_patterns: List[str] = Field(default_factory=lambda: ["rm -rf /", ":(){ :|:& };:"])
    max_length: int = 1000

    @validator("command")
    def validate_command(cls, v, values):
        """Validate command."""
        # Check length
        if len(v) > values.get("max_length", 1000):
            raise ValueError(f"Command too long (max {values.get('max_length')} characters)")

        # Check forbidden patterns
        forbidden = values.get("forbidden_patterns", [])
        for pattern in forbidden:
            if pattern in v:
                raise ValueError(f"Forbidden pattern found: {pattern}")

        return v

    def sanitize(self) -> str:
        """Get sanitized command."""
        return InputSanitizer.sanitize_command(self.command)


class APIKeyModel(BaseModel):
    """Model for API key validation."""
    key: str
    prefix: Optional[str] = None
    min_length: int = 20
    max_length: int = 200

    @validator("key")
    def validate_key(cls, v, values):
        """Validate API key."""
        # Check length
        min_len = values.get("min_length", 20)
        max_len = values.get("max_length", 200)
        if not min_len <= len(v) <= max_len:
            raise ValueError(f"Key length must be between {min_len} and {max_len}")

        # Check prefix if specified
        prefix = values.get("prefix")
        if prefix and not v.startswith(prefix):
            raise ValueError(f"Key must start with {prefix}")

        # Check for valid characters
        if not re.match(r"^[A-Za-z0-9_-]+$", v):
            raise ValueError("Key contains invalid characters")

        return v


class ConfigValidator:
    """Validate configuration objects."""

    def __init__(self, schema: Dict[str, Type]):
        self.schema = schema

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate configuration dictionary."""
        result = ValidationResult(valid=True)

        # Check required fields
        for key, expected_type in self.schema.items():
            if key not in config:
                result.valid = False
                result.errors.append(f"Missing required field: {key}")
                continue

            # Validate type
            value = config[key]
            if not TypeValidator.validate_type(value, expected_type):
                result.valid = False
                result.errors.append(
                    f"Field '{key}' has wrong type. Expected {expected_type}, got {type(value)}"
                )

        # Check for unknown fields
        unknown = set(config.keys()) - set(self.schema.keys())
        if unknown:
            result.warnings.append(f"Unknown fields: {unknown}")

        return result


class CompositeValidator:
    """Compose multiple validators together."""

    def __init__(self):
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> "CompositeValidator":
        """Add a validation rule."""
        self.rules.append(rule)
        return self

    def add_type_check(
        self,
        name: str,
        expected_type: Type,
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> "CompositeValidator":
        """Add type checking rule."""
        self.rules.append(ValidationRule(
            name=name,
            type=ValidationType.TYPE,
            validator=lambda v: TypeValidator.validate_type(v, expected_type),
            error_message=f"Type check failed for {name}",
            level=level
        ))
        return self

    def add_range_check(
        self,
        name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> "CompositeValidator":
        """Add range checking rule."""
        self.rules.append(ValidationRule(
            name=name,
            type=ValidationType.RANGE,
            validator=lambda v: RangeValidator.validate_range(v, min_value, max_value),
            error_message=f"Range check failed for {name} (must be between {min_value} and {max_value})",
            level=level
        ))
        return self

    def add_pattern_check(
        self,
        name: str,
        pattern: Union[str, re.Pattern],
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> "CompositeValidator":
        """Add pattern matching rule."""
        self.rules.append(ValidationRule(
            name=name,
            type=ValidationType.PATTERN,
            validator=lambda v: PatternValidator.validate(v, pattern),
            error_message=f"Pattern check failed for {name}",
            level=level
        ))
        return self

    def add_custom_check(
        self,
        name: str,
        validator: Callable[[Any], bool],
        error_message: str,
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> "CompositeValidator":
        """Add custom validation rule."""
        self.rules.append(ValidationRule(
            name=name,
            type=ValidationType.CUSTOM,
            validator=validator,
            error_message=error_message,
            level=level
        ))
        return self

    def validate(
        self,
        value: Any,
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ValidationResult:
        """Run all validation rules."""
        result = ValidationResult(valid=True)

        for rule in self.rules:
            # Skip rules above current level
            if rule.level.value > level.value:
                continue

            try:
                if not rule.validator(value):
                    result.valid = False
                    result.errors.append(rule.error_message)
            except Exception as e:
                result.valid = False
                result.errors.append(f"Validation error in {rule.name}: {e}")

        return result


# Factory functions for common validators

def create_file_validator() -> CompositeValidator:
    """Create a validator for file operations."""
    return (
        CompositeValidator()
        .add_type_check("path", str)
        .add_custom_check(
            "safe_path",
            lambda p: ".." not in Path(p).parts,
            "Path contains directory traversal"
        )
        .add_custom_check(
            "no_null_bytes",
            lambda p: "\x00" not in p,
            "Path contains null bytes"
        )
    )


def create_command_validator() -> CompositeValidator:
    """Create a validator for shell commands."""
    return (
        CompositeValidator()
        .add_type_check("command", str)
        .add_range_check("length", min_value=1, max_value=10000)
        .add_custom_check(
            "no_dangerous",
            lambda c: not any(danger in c for danger in ["rm -rf /", ":(){ :|:& };:"]),
            "Command contains dangerous patterns"
        )
    )


def create_api_key_validator(prefix: str = "") -> CompositeValidator:
    """Create a validator for API keys."""
    validator = (
        CompositeValidator()
        .add_type_check("key", str)
        .add_range_check("length", min_value=20, max_value=200)
        .add_pattern_check("format", r"^[A-Za-z0-9_-]+$")
    )

    if prefix:
        validator.add_custom_check(
            "prefix",
            lambda k: k.startswith(prefix),
            f"API key must start with {prefix}"
        )

    return validator


def create_url_validator() -> CompositeValidator:
    """Create a validator for URLs."""
    return (
        CompositeValidator()
        .add_type_check("url", str)
        .add_pattern_check("format", "url")
        .add_custom_check(
            "protocol",
            lambda u: u.startswith(("http://", "https://")),
            "URL must use HTTP or HTTPS protocol"
        )
    )


def create_email_validator() -> CompositeValidator:
    """Create a validator for email addresses."""
    return (
        CompositeValidator()
        .add_type_check("email", str)
        .add_pattern_check("format", "email")
        .add_range_check("length", min_value=3, max_value=320)
    )


# Decorator for function argument validation

def validate_args(**validators: CompositeValidator):
    """Decorator to validate function arguments."""
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for arg_name, validator in validators.items():
                if arg_name in bound.arguments:
                    value = bound.arguments[arg_name]
                    result = validator.validate(value)
                    if not result.valid:
                        raise ValueError(
                            f"Validation failed for argument '{arg_name}': {', '.join(result.errors)}"
                        )

            return func(*args, **kwargs)

        return wrapper
    return decorator


# Example usage:
# @validate_args(
#     path=create_file_validator(),
#     command=create_command_validator()
# )
# def process_file(path: str, command: str) -> None:
#     # Arguments are already validated
#     pass