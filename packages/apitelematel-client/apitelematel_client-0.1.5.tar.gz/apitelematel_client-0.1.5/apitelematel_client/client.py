"""Implementa el cliente HTTP ligero para apitelematel."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from requests import Session

from .config import ClientSettings
from .exceptions import ApiTelematelClientError, ApiTelematelServerError

DEFAULT_HEADERS = {"Content-Type": "application/json"}


class ApiTelematelClient:
    """Clase principal que expone operaciones disponibles en la API."""

    API_PREFIX = "/api/v1.0"

    def __init__(
        self,
        settings: Optional[ClientSettings] = None,
        base_url: Optional[str] = None,
        secret_key: Optional[str] = None,
        timeout: Optional[float] = None,
        session: Optional[Session] = None,
    ) -> None:
        if settings is None:
            if not base_url or not secret_key:
                raise ApiTelematelClientError(
                    "Debe proporcionar un base_url y un secret_key o un ClientSettings preconfigurado"
                )
            settings = ClientSettings(base_url=base_url, secret_key=secret_key, timeout=timeout)

        self._settings = settings
        self._session = session or requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {**DEFAULT_HEADERS}
        headers["X-Secret-Key"] = self._settings.secret_key
        return headers

    def _build_url(self, path: str) -> str:
        if not self._settings.base_url:
            raise ApiTelematelClientError("No hay un base_url configurado para el cliente")
        return f"{self._settings.base_url.rstrip('/')}{path}"

    def _request(self, path: str, payload: Dict[str, Any]) -> Any:
        url = self._build_url(path)
        try:
            response = self._session.post(
                url,
                json=payload,
                headers=self._headers(),
                timeout=self._settings.timeout,
            )
        except requests.RequestException as exc:
            raise ApiTelematelClientError("Error de conexión con apitelematel", original=exc)

        if response.status_code >= 500:
            raise ApiTelematelServerError("Error inesperado en el servidor apitelematel")

        if not response.ok:
            raise ApiTelematelClientError(
                "La API respondió con un error", status_code=response.status_code
            )

        return response.json()

    def query(
        self,
        sql: str,
        connection_key: Optional[str] = None,
        dsn: Optional[str] = None,
    ) -> Any:
        """Ejecuta una consulta SQL/ODBC en el endpoint /api_v1.0/query."""
        payload: Dict[str, Any] = {"query": sql}
        if connection_key:
            payload["connection_key"] = connection_key
        if dsn:
            payload["dsn"] = dsn
        return self._request(f"{self.API_PREFIX}/query", payload)

    def get_cliente(self, cod_cli: str, connection_key: Optional[str] = None) -> Any:
        """Obtiene la ficha del cliente pasando `cod_cli` al endpoint /clientes."""
        payload: Dict[str, Any] = {"cod_cli": cod_cli}
        if connection_key:
            payload["connection_key"] = connection_key
        return self._request(f"{self.API_PREFIX}/clientes", payload)
