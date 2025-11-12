"""Carga y valida ajustes usados por el cliente."""

from __future__ import annotations

import os
from dataclasses import dataclass
from os import PathLike
from typing import Mapping, Optional, Union

DEFAULT_TIMEOUT = 15.0


@dataclass
class ClientSettings:
    """Agrupa la configuración mínima para comunicar con la API."""

    base_url: str
    secret_key: str
    timeout: float = DEFAULT_TIMEOUT

    @classmethod
    def from_env(
        cls,
        env: Optional[Mapping[str, str]] = None,
        base_url_var: str = "APITELEMATEL_BASE_URL",
        secret_key_var: str = "APITELEMATEL_SECRET_KEY",
    ) -> "ClientSettings":
        """Crea la configuración leyendo las variables de entorno en español."""
        env = env or os.environ
        base_url = env.get(base_url_var)
        secret_key = env.get(secret_key_var)
        if not base_url or not secret_key:
            raise ValueError("Faltan APITELEMATEL_BASE_URL o APITELEMATEL_SECRET_KEY en el entorno")
        timeout = _parse_timeout(env)
        return cls(base_url=base_url, secret_key=secret_key, timeout=timeout)


def _parse_timeout(env: Mapping[str, str]) -> float:
    raw_timeout = env.get("APITELEMATEL_TIMEOUT")
    if not raw_timeout:
        return DEFAULT_TIMEOUT
    try:
        return float(raw_timeout)
    except ValueError as exc:
        raise ValueError("APITELEMATEL_TIMEOUT debe ser un número") from exc
