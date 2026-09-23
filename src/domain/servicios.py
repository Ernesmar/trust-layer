"""Casos de uso. Cada clase orquesta puertos, nunca implementa infraestructura."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from .hash_chain import GENESIS_HASH, calcular_hash
from .models import AgenteIA, RegistroAuditable
from .ports import FirmadorCriptografico, RepositorioAgentes, RepositorioRegistros


class VerificarIdentidadAgente:
    """Caso de uso: registra un nuevo agente y devuelve su identidad."""

    def __init__(self, repo_agentes: RepositorioAgentes) -> None:
        self._repo_agentes = repo_agentes

    def ejecutar(self, empresa_propietaria: str, proposito_declarado: str, permisos: list[str]) -> AgenteIA:
        agente = AgenteIA.nuevo(empresa_propietaria, proposito_declarado, permisos)
        self._repo_agentes.guardar(agente)
        return agente


class AgenteNoEncontradoError(Exception):
    pass


class RegistrarAccionAuditable:
    """Caso de uso: añade una entrada inmutable al log de un agente."""

    def __init__(
        self,
        repo_agentes: RepositorioAgentes,
        repo_registros: RepositorioRegistros,
        firmador: FirmadorCriptografico,
    ) -> None:
        self._repo_agentes = repo_agentes
        self._repo_registros = repo_registros
        self._firmador = firmador

    def ejecutar(self, agente_id: str, accion: str, objetivo: str) -> RegistroAuditable:
        if self._repo_agentes.obtener(agente_id) is None:
            raise AgenteNoEncontradoError(f"agente {agente_id} no está registrado")

        hash_anterior = self._repo_registros.ultimo_hash_de(agente_id) or GENESIS_HASH
        registro_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC)

        # payload canónico calculado igual que RegistroAuditable.payload_canonico,
        # necesario aquí para poder firmar antes de construir el objeto final
        payload_canonico = "|".join(
            [registro_id, agente_id, accion, objetivo, timestamp.isoformat(), hash_anterior]
        )
        hash_actual = calcular_hash(payload_canonico, hash_anterior)
        firma = self._firmador.firmar(payload_canonico, hash_actual)

        registro = RegistroAuditable(
            registro_id=registro_id,
            agente_id=agente_id,
            accion=accion,
            objetivo=objetivo,
            timestamp=timestamp,
            hash_anterior=hash_anterior,
            hash_actual=hash_actual,
            firma=firma,
        )
        self._repo_registros.anexar(registro)
        return registro
