"""Puertos: contratos que el dominio exige, la infraestructura los cumple.

Nada aquí sabe de Postgres, MCP, ni HTTP. Eso es justo lo que permite
testear el dominio con adaptadores en memoria y cambiar de base de datos
sin tocar la lógica de negocio.
"""
from __future__ import annotations

from typing import Protocol

from .models import AgenteIA, RegistroAuditable


class RepositorioAgentes(Protocol):
    def guardar(self, agente: AgenteIA) -> None: ...
    def obtener(self, agente_id: str) -> AgenteIA | None: ...


class RepositorioRegistros(Protocol):
    def anexar(self, registro: RegistroAuditable) -> None: ...
    def ultimo_hash_de(self, agente_id: str) -> str: ...
    def historial_de(self, agente_id: str) -> list[RegistroAuditable]: ...


class FirmadorCriptografico(Protocol):
    def firmar(self, payload_canonico: str, hash_actual: str) -> str: ...
    def clave_secreta(self) -> bytes: ...
