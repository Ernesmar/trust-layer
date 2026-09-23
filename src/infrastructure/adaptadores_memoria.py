"""Adaptadores en memoria. Implementan los puertos del dominio sin DB real.

Su único propósito es permitir tests unitarios rápidos del dominio y
servir de referencia de comportamiento para el adaptador de Postgres
(los mismos tests de integración deben poder correr contra ambos).
"""
from __future__ import annotations

from src.domain.hash_chain import GENESIS_HASH, firmar
from src.domain.models import AgenteIA, RegistroAuditable


class RepositorioAgentesMemoria:
    def __init__(self) -> None:
        self._agentes: dict[str, AgenteIA] = {}

    def guardar(self, agente: AgenteIA) -> None:
        self._agentes[agente.agente_id] = agente

    def obtener(self, agente_id: str) -> AgenteIA | None:
        return self._agentes.get(agente_id)


class RepositorioRegistrosMemoria:
    def __init__(self) -> None:
        self._registros: dict[str, list[RegistroAuditable]] = {}

    def anexar(self, registro: RegistroAuditable) -> None:
        self._registros.setdefault(registro.agente_id, []).append(registro)

    def ultimo_hash_de(self, agente_id: str) -> str:
        historial = self._registros.get(agente_id, [])
        return historial[-1].hash_actual if historial else GENESIS_HASH

    def historial_de(self, agente_id: str) -> list[RegistroAuditable]:
        return list(self._registros.get(agente_id, []))


class FirmadorMemoria:
    """Firmador determinista para tests — NUNCA usar esta clave en producción."""

    def __init__(self, clave_secreta: bytes = b"clave-de-test-no-usar-en-produccion") -> None:
        self._clave = clave_secreta

    def firmar(self, payload_canonico: str, hash_actual: str) -> str:
        return firmar(payload_canonico, hash_actual, self._clave)

    def clave_secreta(self) -> bytes:
        return self._clave
