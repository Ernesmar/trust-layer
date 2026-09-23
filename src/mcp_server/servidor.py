"""Adaptador MCP. Traduce llamadas de herramienta a casos de uso del dominio.

Deliberadamente delgado: si hay lógica de negocio aquí, está en el lugar
equivocado — debe vivir en src/domain/servicios.py.
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from src.domain.hash_chain import CadenaAlteradaError, verificar_cadena
from src.domain.servicios import AgenteNoEncontradoError, RegistrarAccionAuditable, VerificarIdentidadAgente
from src.infrastructure.adaptadores_memoria import (
    FirmadorMemoria,
    RepositorioAgentesMemoria,
    RepositorioRegistrosMemoria,
)

# Fase 1 arranca con adaptadores en memoria; cambiar a Postgres es solo
# sustituir estas tres líneas por los adaptadores reales, el dominio no cambia.
_repo_agentes = RepositorioAgentesMemoria()
_repo_registros = RepositorioRegistrosMemoria()
_firmador = FirmadorMemoria()

_verificar_identidad = VerificarIdentidadAgente(_repo_agentes)
_registrar_accion = RegistrarAccionAuditable(_repo_agentes, _repo_registros, _firmador)

mcp = MCPServer("registro-de-confianza-agentes")


@mcp.tool()
def verificar_identidad_agente(
    empresa_propietaria: str, proposito_declarado: str, permisos: list[str]
) -> dict:
    """Registra un nuevo agente de IA y devuelve su identidad verificable."""
    agente = _verificar_identidad.ejecutar(empresa_propietaria, proposito_declarado, permisos)
    return {
        "agente_id": agente.agente_id,
        "empresa_propietaria": agente.empresa_propietaria,
        "proposito_declarado": agente.proposito_declarado,
        "permisos": list(agente.permisos),
        "creado_en": agente.creado_en.isoformat(),
    }


@mcp.tool()
def registrar_accion_auditable(agente_id: str, accion: str, objetivo: str) -> dict:
    """Añade una entrada inmutable y firmada al log de acciones de un agente."""
    try:
        registro = _registrar_accion.ejecutar(agente_id, accion, objetivo)
    except AgenteNoEncontradoError as exc:
        return {"error": str(exc)}
    return {
        "registro_id": registro.registro_id,
        "agente_id": registro.agente_id,
        "accion": registro.accion,
        "objetivo": registro.objetivo,
        "timestamp": registro.timestamp.isoformat(),
        "hash_actual": registro.hash_actual,
    }


@mcp.tool()
def verificar_historial(agente_id: str) -> dict:
    """Recalcula la cadena completa de un agente y confirma que no fue alterada."""
    historial = _repo_registros.historial_de(agente_id)
    try:
        verificar_cadena(historial, _firmador.clave_secreta())
    except CadenaAlteradaError as exc:
        return {"integro": False, "detalle": str(exc)}
    return {"integro": True, "cantidad_registros": len(historial)}


if __name__ == "__main__":
    mcp.run()
