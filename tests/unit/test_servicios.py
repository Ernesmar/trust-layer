import pytest

from src.domain.servicios import AgenteNoEncontradoError, RegistrarAccionAuditable, VerificarIdentidadAgente
from src.infrastructure.adaptadores_memoria import (
    FirmadorMemoria,
    RepositorioAgentesMemoria,
    RepositorioRegistrosMemoria,
)


@pytest.fixture
def contexto():
    repo_agentes = RepositorioAgentesMemoria()
    repo_registros = RepositorioRegistrosMemoria()
    firmador = FirmadorMemoria()
    return {
        "verificar_identidad": VerificarIdentidadAgente(repo_agentes),
        "registrar_accion": RegistrarAccionAuditable(repo_agentes, repo_registros, firmador),
        "repo_registros": repo_registros,
    }


def test_registrar_agente_devuelve_identidad_valida(contexto):
    agente = contexto["verificar_identidad"].ejecutar(
        empresa_propietaria="Acme SRL",
        proposito_declarado="clasificar tickets de soporte",
        permisos=["leer_tickets"],
    )
    assert agente.agente_id
    assert agente.empresa_propietaria == "Acme SRL"


def test_registrar_agente_sin_empresa_falla(contexto):
    with pytest.raises(ValueError):
        contexto["verificar_identidad"].ejecutar("", "algo", [])


def test_registrar_accion_de_agente_inexistente_falla(contexto):
    with pytest.raises(AgenteNoEncontradoError):
        contexto["registrar_accion"].ejecutar("id-que-no-existe", "leer", "api/tickets")


def test_dos_acciones_seguidas_encadenan_hash(contexto):
    agente = contexto["verificar_identidad"].ejecutar("Acme SRL", "clasificar tickets", [])
    r1 = contexto["registrar_accion"].ejecutar(agente.agente_id, "leer", "api/tickets")
    r2 = contexto["registrar_accion"].ejecutar(agente.agente_id, "escribir", "api/tickets/42")

    assert r2.hash_anterior == r1.hash_actual
    assert r2.hash_actual != r1.hash_actual
