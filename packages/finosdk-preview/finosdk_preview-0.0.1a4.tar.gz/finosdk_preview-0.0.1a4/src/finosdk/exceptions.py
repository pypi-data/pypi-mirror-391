# D:\prog\finosdk\src\finosdk\exceptions.py
from typing import Optional


class FinoError(Exception):
    """Base SDK error."""


class FinoHTTPError(FinoError):
    def __init__(self, status: int, text: str):
        super().__init__(f"HTTP {status}: {text}")
        self.status = status
        self.text = text


class FinoAPIError(FinoError):
    def __init__(self, msg: Optional[str], payload=None):
        super().__init__(msg or "API error")
        self.payload = payload


class FinoValidationError(FinoError):
    """Client-side validation error (e.g., non-array arguments)."""
    pass
