"""Custom exceptions for SpotKit with clear, actionable error messages."""


class SpotKitError(Exception):
    """Base exception for all SpotKit errors."""

    def __init__(self, message: str, details: str = None, action: str = None):
        self.message = message
        self.details = details
        self.action = action
        super().__init__(self.format_message())

    def format_message(self) -> str:
        parts = [self.message]
        if self.details:
            parts.append(f"\nDetails: {self.details}")
        if self.action:
            parts.append(f"\nAction: {self.action}")
        return "".join(parts)


class SpotKitAuthError(SpotKitError):
    """Authentication and authorization errors."""

    def __init__(self, message: str = None, details: str = None):
        super().__init__(
            message or "Spotify authentication failed",
            details,
            "Run 'spotkit auth' to authenticate",
        )


class SpotKitAPIError(SpotKitError):
    """Spotify API communication errors."""

    def __init__(self, message: str, status_code: int = None, details: str = None):
        self.status_code = status_code
        action = self._get_action(status_code)
        super().__init__(message, details, action)

    def _get_action(self, status_code: int) -> str:
        actions = {
            401: "Run 'spotkit auth' to refresh your credentials",
            403: "Check your Spotify app permissions",
            404: "Verify the resource ID or name is correct",
            429: "Wait a few minutes before retrying (rate limit hit)",
            500: "Spotify API is experiencing issues - try again later",
            503: "Spotify API is temporarily unavailable - retry in a few minutes",
        }
        return actions.get(status_code, "Check your internet connection and try again")


class SpotKitConfigError(SpotKitError):
    """Configuration file errors."""

    def __init__(self, missing_key: str = None, details: str = None):
        if missing_key:
            message = f"Missing configuration: {missing_key}"
            action = f"Add '{missing_key}' to ~/.spotkit/config.json or set via environment variable"
        else:
            message = "Configuration error"
            action = "Check ~/.spotkit/config.json for valid JSON format"
        super().__init__(message, details, action)


class SpotKitStorageError(SpotKitError):
    """Database and file storage errors."""

    def __init__(self, operation: str = None, details: str = None):
        message = (
            f"Storage operation failed: {operation}" if operation else "Database error"
        )
        action = "Check ~/.spotkit/ directory permissions and disk space"
        super().__init__(message, details, action)


class SpotKitValidationError(SpotKitError):
    """Input validation errors."""

    def __init__(self, field: str, value: any, constraint: str):
        message = f"Invalid {field}: {value}"
        super().__init__(message, f"Expected: {constraint}", None)


class SpotKitResourceNotFoundError(SpotKitError):
    """Resource not found errors."""

    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} not found: {identifier}"
        action = f"Use 'spotkit list-{resource_type.lower()}s' to see available {resource_type.lower()}s"
        super().__init__(message, None, action)
