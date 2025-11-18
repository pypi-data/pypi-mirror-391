class APIError(Exception):
    """Represents API-level errors returned by the Vector DB service."""

    def __init__(self, status_code: int, message: str):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.message = message
