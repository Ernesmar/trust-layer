"""Entidades del dominio. Sin dependencias externas: nada de DB, nada de red."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class AgenteIA:
    """Identidad registrada de un agente de IA."""

    agente_id: str
    empresa_propietaria: str
    proposito_declarado: str
    permisos: tuple[str, ...]
    creado_en: datetime = field(default_factory=_now)

    @staticmethod
    def nuevo(empresa_propietaria: str, proposito_declarado: str, permisos: list[str]) -> AgenteIA:
        if not empresa_propietaria.strip():
            raise ValueError("empresa_propietaria no puede estar vacío")
        if not proposito_declarado.strip():
            raise ValueError("proposito_declarado no puede estar vacío")
        return AgenteIA(
            agente_id=str(uuid.uuid4()),
            empresa_propietaria=empresa_propietaria,
            proposito_declarado=proposito_declarado,
            permisos=tuple(permisos),
        )


@dataclass(frozen=True)
class RegistroAuditable:
    """Una entrada inmutable en el log de acciones de un agente.

    hash_actual siempre depende de hash_anterior: esto es lo que hace
    la cadena verificable (tamper-evident). Ver domain/hash_chain.py.
    """

    registro_id: str
    agente_id: str
    accion: str
    objetivo: str
    timestamp: datetime
    hash_anterior: str
    hash_actual: str
    firma: str

    @property
    def payload_canonico(self) -> str:
        """Representación determinista usada para firmar y encadenar."""
        return "|".join(
            [
                self.registro_id,
                self.agente_id,
                self.accion,
                self.objetivo,
                self.timestamp.isoformat(),
                self.hash_anterior,
            ]
        )
