"""Contract tests: si esto se rompe, cualquier cliente MCP que consuma el
servidor recibe un schema distinto al esperado. Es la red de seguridad del
'contrato' con quien integra este servicio, no solo con quien lo escribe."""
from src.mcp_server.servidor import (
    registrar_accion_auditable,
    verificar_historial,
    verificar_identidad_agente,
)

CAMPOS_ESPERADOS_IDENTIDAD = {
    "agente_id", "empresa_propietaria", "proposito_declarado", "permisos", "creado_en",
}
CAMPOS_ESPERADOS_REGISTRO = {
    "registro_id", "agente_id", "accion", "objetivo", "timestamp", "hash_actual",
}
CAMPOS_ESPERADOS_VERIFICACION = {"integro", "cantidad_registros"}


def test_contrato_verificar_identidad_agente():
    resultado = verificar_identidad_agente(
        empresa_propietaria="Acme SRL", proposito_declarado="procesar pagos", permisos=["leer"]
    )
    assert set(resultado.keys()) == CAMPOS_ESPERADOS_IDENTIDAD


def test_contrato_registrar_accion_auditable():
    agente = verificar_identidad_agente(
        empresa_propietaria="Acme SRL", proposito_declarado="procesar pagos", permisos=["leer"]
    )
    resultado = registrar_accion_auditable(
        agente_id=agente["agente_id"], accion="leer", objetivo="api/saldo"
    )
    assert set(resultado.keys()) == CAMPOS_ESPERADOS_REGISTRO


def test_contrato_verificar_historial():
    agente = verificar_identidad_agente(
        empresa_propietaria="Acme SRL", proposito_declarado="procesar pagos", permisos=["leer"]
    )
    registrar_accion_auditable(agente_id=agente["agente_id"], accion="leer", objetivo="api/saldo")
    resultado = verificar_historial(agente_id=agente["agente_id"])
    assert set(resultado.keys()) == CAMPOS_ESPERADOS_VERIFICACION
