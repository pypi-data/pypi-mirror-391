"""Excepciones específicas para el cliente de apitelematel."""

from __future__ import annotations

from typing import Optional


class ApiTelematelClientError(Exception):
    """Error general ocurrido durante las llamadas al API."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, original: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.original = original


class ApiTelematelServerError(ApiTelematelClientError):
    """Error específico cuando el servidor responde con estado >= 500."""

    pass
